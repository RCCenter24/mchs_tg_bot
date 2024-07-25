from icecream import ic
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F, types, Router

from datetime import datetime as dt

import pandas as pd
from utils.df_modifier import modify_dataframe
from utils.message_spitter import split_message
from utils.response_maker import response_maker
from utils.result_df_maker import result_df_maker
from images import main_photo, map_image, support_menu

from database.models import Municipalities, Users, Subscriptions, Messages, Fires
from email_checker import fetch_and_save_files
from bot import bot

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.dialects.postgresql import insert

main_router = Router()


class Form(StatesGroup):
    waiting_for_munic = State()
    pre_support = State()
    support = State()


@main_router.message(F.animation)
async def echo_gif(message: Message):
    file_id = message.animation.file_id

    await message.reply_animation(file_id)


@main_router.message(F.photo)
async def get_photo_id(message: Message):
    await message.reply(text=f"{message.photo[-1].file_id}")

@main_router.message(CommandStart(), F.chat.type == 'private')
async def handle_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    add_user_query = insert(Users).values(
        user_id=user_id,
        first_name=first_name,
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
               "образований для получения новостей воспользуйтесь командой /subscribe \n Чтобы подписаться "
               "на все обновления нажмите на команду /subscribe_all\n")

    await message.answer_photo(caption=caption, reply_markup=markup, photo=main_photo)


@main_router.message(Command('help'), F.chat.type == 'private')
async def handle_waiting_for_choise(message: types.Message):
    response = ('Основные команды:\n\n'
                'выбрать муниципальное образований /subscribe \n'
                'подписаться на все муниципальные обазования /subscribe_all \n'
                'отказаться от всех подписок /cancel_subscriptions \n'
                'посмотреть мои подписки /my_subscriptions\n'
                'обратиться в техническую поддержку /support')
    await message.answer(response, parse_mode='HTML')


@main_router.message(Command('subscribe'), F.chat.type == 'private')
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
        resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="Выберите муниципальное образование")

    await message.answer_photo(caption='Выберите муниципальное образование',
                               reply_markup=keyboard_1, photo=map_image, parse_mode='HTML')

    await state.set_state(Form.waiting_for_munic)

    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])


@main_router.message(StateFilter(Form.waiting_for_munic), F.chat.type == 'private')
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

        subscribe_check_query = select(Subscriptions.municipality_id) \
            .join(Municipalities, Municipalities.municipality_id == Subscriptions.municipality_id) \
            .where(
                (Subscriptions.user_id == user_id) &
                (Municipalities.municipality_name == selected_mun)
            )

        result = await session.execute(subscribe_check_query)
        subscription_exists = result.first()

        if subscription_exists is not None:
            await message.answer('Вы уже подписаны на это муниципальное образование',
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            subquery = select(Municipalities.municipality_id).where(
                Municipalities.municipality_name == selected_mun).scalar_subquery()

            add_subscriber_query = insert(Subscriptions).values(
                user_id=user_id,
                municipality_id=subquery,
                date_subscribed=dt.now()
            ).on_conflict_do_nothing()

            await session.execute(add_subscriber_query)
            await session.commit()

            query_get_subs = select(Municipalities.municipality_name) \
                    .join(Subscriptions, Subscriptions.municipality_id == Municipalities.municipality_id) \
                    .where(Subscriptions.user_id == user_id)

            result = await session.execute(query_get_subs)
            all_cathegories = result.all()

            municipalities = [item[0] for item in all_cathegories]

            message_text = "Подписка прошла успешно 🙂\n\n<b>Ваши подписки</b>\n" + \
                "\n".join(municipalities)

            await message.answer(message_text, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')


@main_router.message(Command('subscribe_all'), F.chat.type == 'private')
async def handle_sub_to_all_munic(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id

    subscribe_query = select(Municipalities.municipality_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    municipality_ids = [item[0] for item in all_municipalities]
    municipality_names = [item[1] for item in all_municipalities]
    subscribers_data = [
        {
            "user_id": user_id,
            "municipality_id": municipality_ids,
            "date_subscribed": dt.now()
        }
        for municipality_ids, municipality_name in zip(municipality_ids, municipality_names)
    ]
    add_subscriber_query = insert(Subscriptions).values(
        subscribers_data).on_conflict_do_nothing()
    await session.execute(add_subscriber_query)
    await session.commit()

    await message.answer('Вы подписались на все муниципальные образования')


@main_router.message(Command('my_subscriptions'), F.chat.type == 'private')
async def handle_my_subscriptions(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id

    query_get_subs = select(Municipalities.municipality_name) \
                    .join(Subscriptions, and_(Subscriptions.municipality_id == Municipalities.municipality_id,
                                              Subscriptions.user_id == user_id))
                    
    result = await session.execute(query_get_subs)
    all_cathegories = result.all()

    municipalities = [item[0] for item in all_cathegories]

    if municipalities == []:
        response = ('У вас нет активных подписок, чтобы подписаться нажмите /subscribe '
                    'или нажмите /help если нужна помощь')
        await message.answer(response)
        return
    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    try:
        await message.answer_photo(caption=message_text, photo=main_photo, parse_mode='HTML')
    except:
        msg_parts = await split_message(message_text)
        for parts in msg_parts:
            await message.answer(parts, parse_mode='HTML')


@main_router.message(Command('cancel_subscriptions'), F.chat.type == 'private')
async def handle_cancel_all_subscriptions(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id
    delete_subs = delete(Subscriptions).where(Subscriptions.user_id == user_id)
    await session.execute(delete_subs)
    await session.commit()
    await message.answer('Вы отписались от всего😕')

@main_router.message(Command('support'), F.chat.type == 'private')
async def handle_cancel_all_subscriptions(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(Form.support)
    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='В главное меню', callback_data='main_menu')]
    ])

    builder.adjust(1)
    builder.attach(InlineKeyboardBuilder.from_markup(markup))
    caption = ('Напишите свое сообщение в техническую поддержку или вернитесь в главное меню')
    
    await message.answer_photo(photo=support_menu, caption = caption, reply_markup=markup)
    

@main_router.message(Command('last_news'), F.chat.type == 'private')
async def manual_check_news(message: Message, session: AsyncSession):
    email_id = await fetch_and_save_files(session)
    user_id = message.from_user.id
    df_query = select(Fires.region, Fires.fire_status, Fires.fire_num,
                      Fires.forestry_name, Fires.forces_aps, Fires.forces_lps,
                      Fires.city, Fires.distance, Fires.map_id, Fires.fire_area, Fires.fire_zone, Fires.ext_log) \
                    .where(Fires.email_id == email_id)
    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    modified_df = await modify_dataframe(df_1)
    subscribers_query = select(Subscriptions.user_id, Subscriptions, Municipalities.map_id) \
                    .join(Municipalities, Subscriptions.municipality_id == Municipalities.municipality_id) \
                    .where(Subscriptions.user_id == user_id)
                           
    result = await session.execute(subscribers_query)
    subscribers = result.all()
    if subscribers == []:
        text = (
                "Для выбранных муниципальных образований информация о пожарной обстановке отсутствует. \n"
                "Чтобы подписаться на другие муниципальные образования нажмите /subscribe или /subscribe_all")
        await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
        return
    df_2 = pd.DataFrame(subscribers)
    result_df = await result_df_maker(modified_df, df_2)

    if not result_df.empty:
        grouped_df = result_df.groupby('user_id')
        for user_id, group in grouped_df:
            group = group.drop_duplicates(subset=['region', 'fire_status', 'fire_num',
                                                  'forestry_name', 'forces_aps', 'forces_lps',
                                                  'city', 'distance', 'map_id', 'fire_area', 'fire_zone'])
            
            grouped_by_municipality = group.groupby('region')
            response = await response_maker(grouped_by_municipality)
            messages = await split_message(response)
            for msg in messages:                
                try:
                    await bot.send_message(chat_id=user_id, text=msg, parse_mode='HTML')
                    
                    sent_message_query = insert(Messages).values(
                        user_id=user_id,
                        email_id=email_id,
                        message_text=response,
                        date_send=dt.now()
                    ).on_conflict_do_nothing()
                    await session.execute(sent_message_query)
                    await session.commit()
                except SQLAlchemyError as db_err:
                    logging.error(
                        f'Ошибка базы данных при обработке пользователя {user_id}: {db_err}')
                    await session.rollback()
                except Exception as e:
                    await bot.send_message(chat_id=user_id, text='Не удалось отправить сообщение', parse_mode='HTML')
                    logging.error(
                        f'Ошибка при отправке пользователю {user_id}: {str(e)}')

                