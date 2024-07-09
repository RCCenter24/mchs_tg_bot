from icecream import ic
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F, types, Router

from glob import glob
import os

from datetime import datetime as dt

import pandas as pd
from utils.df_converter import df_converter
from utils.df_modifier import df_mod
from utils.result_df_maker import result_df_maker
from images import main_photo, map_image

from database.models import Municipalities, Users, Subscriptions, Messages
from email_checker import fetch_and_save_files
from bot import bot

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

main_router = Router()


class Form(StatesGroup):
    waiting_for_munic = State()



@main_router.message(F.animation)
async def echo_gif(message: Message):
    file_id = message.animation.file_id
    
    await message.reply_animation(file_id)
    
@main_router.message(F.photo)
async def get_photo_id(message: Message):
    await message.reply(text=f"{message.photo[-1].file_id}")



@main_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    add_user_query = insert(Users).values(
        user_id=user_id,
        user_name=first_name,
        last_name=last_name,
        username=username,
        joined_at=dt.now()
    ).on_conflict_do_nothing()

    await session.execute(add_user_query)
    await session.commit()

    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Выбрать муниципальное образование', callback_data='choise_munic')],
        [InlineKeyboardButton(
            text='Подписаться на все обновления', callback_data='choise_all_munic')]
    ])

    builder.adjust(1)
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    caption = ("Это бот по инцидентам МЧС Красноярского края. Чтобы подписаться на одно из муниципальных "
               "образований для получения новостей воспользуйтесь командой /subscribe \n Чтобы подписатья "
               "на все обновления нажмите на команду /subscribe_all\n")
                
    
    await message.answer_photo(caption= caption, reply_markup=markup, photo=main_photo)



@main_router.message(Command('help'))
async def handle_waiting_for_choise(message: types.Message):
    response = ('Основные команды:\n\n'
                'выбрать муниципальное образований /subscribe \n'
                'подписаться на все муниципальные обазования /subscribe_all \n'
                'отказаться от всех подписок /cancel_subscriptions \n'
                'посмотреть мои подписки /my_subscriptions')
    await message.answer(response, parse_mode='HTML')


@main_router.message(Command('subscribe'))
async def handle_waiting_for_choise(message: types.Message, state: FSMContext, session: AsyncSession):

    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()

    builder = ReplyKeyboardBuilder()

    for _, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]
        builder.button(text=button_text)
    builder.button(text='Отмена')
    builder.adjust(1)
    keyboard_1 = builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберите муниципальное образование")

    try:
        await message.edit_caption(caption='Выберите муниципальное образование')
    except:
        await message.answer_photo(caption='Выберите муниципальное образование',
                                   reply_markup=keyboard_1, photo = map_image, parse_mode='HTML')
    
    await state.set_state(Form.waiting_for_munic)

    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])


@main_router.message(StateFilter(Form.waiting_for_munic))
async def subscribe(message: types.Message, state: FSMContext, session: AsyncSession):
    selected_mun = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    if selected_mun == "Отмена":
        await state.clear()
        await message.answer('Вы вернулись в главное меню', reply_markup=types.ReplyKeyboardRemove())
        return

    all_municipalities = data.get('all_municipalities', [])
    if selected_mun in all_municipalities:

        subscribe_check_query = select(Subscriptions.map_id).where(
            (Subscriptions.user_id == user_id) &
            (Subscriptions.municipality_name == selected_mun)
        )

        result = await session.execute(subscribe_check_query)
        subscription_exists = result.first()

        if subscription_exists is not None:
            await message.answer('Вы уже подписаны на это муниципальное образование')
        else:
            subquery = select(Municipalities.map_id).where(
                Municipalities.municipality_name == selected_mun).scalar_subquery()

            add_subscriber_query = insert(Subscriptions).values(
                user_id=user_id,
                map_id=subquery.scalar_subquery(),
                municipality_name=selected_mun,
                subscribed_at=dt.now()
            ).on_conflict_do_nothing()

            await session.execute(add_subscriber_query)
            await session.commit()

            query_get_subs = select(Subscriptions.municipality_name).where(
                Subscriptions.user_id == user_id)

            result = await session.execute(query_get_subs)
            all_cathegories = result.all()

            municipalities = [item[0] for item in all_cathegories]

            message_text = "Подписка прошла успешно 🙂\n\n<b>Ваши подписки</b>\n" + \
                "\n".join(municipalities)

            await message.answer(message_text, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')



@main_router.message(Command('subscribe_all'))
async def handle_sub_to_all_munic(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    
    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    map_ids = [item[0] for item in all_municipalities]
    municipality_names  = [item[1] for item in all_municipalities]
    subscribers_data = [
        {
            "user_id": user_id,
            "map_id": map_id,
            "municipality_name": municipality_name,
            "subscribed_at": dt.now()
        }
        for map_id, municipality_name in zip(map_ids, municipality_names)
    ]
    add_subscriber_query = insert(Subscriptions).values(subscribers_data).on_conflict_do_nothing()
    await session.execute(add_subscriber_query)
    await session.commit()
    
    await message.answer('Вы подписались на все муниципальные образования')




@main_router.message(Command('my_subscriptions'))
async def handle_my_subscriptions(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id

    query_get_subs = select(Subscriptions.municipality_name).where(
        Subscriptions.user_id == user_id)
    result = await session.execute(query_get_subs)
    all_cathegories = result.all()

    municipalities = [item[0] for item in all_cathegories]
    
    if municipalities == []:
        response = ('У вас нет активных подписок, чтобы подписаться нажмите /subscriptions '
                    'или нажмите /help если нужна помощь')
        await message.answer(response)
        return
    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    try:
        await message.answer_photo(caption=message_text, photo=main_photo, parse_mode='HTML')
    except:
        await message.answer(message_text, parse_mode='HTML')


@main_router.message(Command('cancel_subscriptions'))
async def handle_cancel_all_subscriptions(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id
    delete_subs = delete(Subscriptions).where(Subscriptions.user_id == user_id)
    await session.execute(delete_subs)
    await session.commit()

    await message.answer('Вы отписались от всего😕')


@main_router.message(Command('check_news'))
async def check_news(message: Message, session: AsyncSession):

    saved_files, subject, content, email_id = await fetch_and_save_files()
    file_path = glob('saved_files/*инамика*.xlsx')
    file_path.sort(key=os.path.getmtime, reverse=True)
    latest_file_path = file_path[0]
    
    conveted_name = await df_converter(latest_file_path)
    df = await df_mod(conveted_name)

    subscribers_query = select(Subscriptions.user_id, Subscriptions.map_id,
                               Subscriptions.municipality_name, Subscriptions.subscribed_at)
    result = await session.execute(subscribers_query)
    subscribers = result.all()

    df_2 = pd.DataFrame(subscribers)
    result_df = await result_df_maker(df, df_2)
    check_query = select(Messages.user_id).where(
        Messages.message_id == email_id)
    check_result = await session.execute(check_query)
    msg_already_sent = check_result.all()

    sent_user_ids = [row[0] for row in msg_already_sent] if msg_already_sent else []

    if not result_df.empty:
        grouped_df = result_df.groupby('user_id')
        
        for user_id, group in grouped_df:
            
            if user_id in sent_user_ids:
                continue 
            else:
                response = ""
                grouped_by_municipality = group.groupby('Район')
                
                
                for municipality, fires in grouped_by_municipality:
                    response += f"\n<b>{municipality}</b>\n"
                    status_counts = fires['icon_status'].value_counts()
    
                    for status, count in status_counts.items():
                        response += f"{count}{status}  "
                    
                    for idx, row in fires.iterrows():    
                        response += (f"\n\n{row['icon_status']} {row['Статус']} пожар №{row['Номер пожара']} {row['Город']} "
                                     f"на площади {row['Площадь обнаружения пожара']} га."
                                     f"\n⏱️{row['Дата возникновения пожара']}\n{row['Статус']}\n")
                                       
                try:
                    await bot.send_message(chat_id=user_id, text=response, parse_mode='HTML')
                    sent_message_query= insert(Messages).values(
                            user_id=user_id,
                            message_id=email_id,
                            message_text=response,
                            date_of_sending=dt.now()
                        ).on_conflict_do_nothing()
                    await session.execute(sent_message_query)
                    await session.commit()
                except SQLAlchemyError as db_err:
                    logging.error(
                        f'Ошибка базы данных при обработке пользователя {user_id}: {db_err}')
                    await session.rollback()
                except Exception as e:
                    logging.error(
                        f'Ошибка при отправке пользователю {user_id}: {str(e)}')
             


@main_router.message(Command('check_news'))
async def manual_check_news(message: Message, session: AsyncSession):

    saved_files, subject, content, email_id = await fetch_and_save_files()
    file_path = glob('saved_files/*инамика*.xlsx')
    file_path.sort(key=os.path.getmtime, reverse=True)
    latest_file_path = file_path[0]
    conveted_name = await df_converter(latest_file_path)
    df = await df_mod(conveted_name)
    subscribers_query = select(Subscriptions.user_id, Subscriptions.map_id)
    result = await session.execute(subscribers_query)
    subscribers = result.all()
    df_2 = pd.DataFrame(subscribers)
    result_df = await result_df_maker(df, df_2)
    grouped_by_municipality = result_df.groupby('Район')
    response = ''
    for municipality, fires in grouped_by_municipality:
        response += f"\n<b>{municipality}</b>\n\n"

        for idx, row in fires.iterrows():
            response += f"{row['icon_status']} {row['Город']} ({row['Номер пожара']}) \n⏱️"
            f"{row['Дата возникновения пожара']}\n{row['Статус']}\n"
    
    await message.answer(text=response, parse_mode='HTML')




@main_router.message(Command('check_email'))
async def check_email(message: Message, state: FSMContext):
    await fetch_and_save_files()
