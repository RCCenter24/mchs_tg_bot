import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types, Router

from glob import glob
import os

from datetime import datetime as dt
from icecream import ic

import pandas as pd
from utils.df_converter import df_converter
from utils.df_modifier import df_mod
from utils.result_df_maker import result_df_maker

from database.models import Municipalities, Users, Subscriptions, Messages
from email_checker import fetch_and_save_files
from bot import bot
from config import EMAIL, PASSWORD, SAVE_DIR
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

main_router = Router()


class Form(StatesGroup):
    waiting_for_munic = State()


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
            text='Выбрать муниципальное образование', callback_data='choise_munic')]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    await message.answer(text=f'Это бот по инцидентам МЧС\nЧтобы выбрать муниципальное образование нажмите'
                         'на кнопку ниже или команду /subscribe', reply_markup=markup)


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
        resize_keyboard=True, one_time_keyboard=True)

    await message.answer(text='Выберите муниципальное образование', reply_markup=keyboard_1)
    await state.set_state(Form.waiting_for_munic)

    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])


@main_router.message(StateFilter(Form.waiting_for_munic))
async def subscribe(message: types.Message, state: FSMContext, session: AsyncSession):
    selected_mun = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    if selected_mun == "Отмена":
        await state.clear()
        await message.answer('Вы вернулись в главное меню')
        return

    all_municipalities = data.get('all_municipalities', [])
    if selected_mun in all_municipalities:

        subscribe_check_query = select(Subscriptions.map_id).where(
            (Subscriptions.user_id == user_id) &
            (Subscriptions.municipality_name == selected_mun)
        )

        result = await session.execute(subscribe_check_query)
        subscription_exists = result.first()

        if subscription_exists != None:
            await message.answer('Вы уже подписаны на это муниципальное образование.')
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

            await message.answer(message_text, parse_mode='HTML')

        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')


@main_router.message(Command('my_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext, session: AsyncSession):

    await state.clear()
    user_id = message.from_user.id

    query_get_subs = select(Subscriptions.municipality_name).where(
        Subscriptions.user_id == user_id)
    result = await session.execute(query_get_subs)
    all_cathegories = result.all()

    municipalities = [item[0] for item in all_cathegories]

    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    await message.answer(message_text, parse_mode='HTML')


@main_router.message(Command('cancel_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext, session: AsyncSession):
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
    
    subscribers_query = select(Subscriptions.user_id, Subscriptions.map_id)
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
                    response += f"\n<b>{municipality}</b>\n\n"

                    for idx, row in fires.iterrows():
                        response += f"{row['icon_status']} {row['Город']} ({row['Номер пожара']}) \n⏱️{row['Дата возникновения пожара']}\n{row['Статус']}\n\n"

                user_ids = [user_id]
                for i in user_ids:
                    try:
                        await bot.send_message(chat_id=i, text=response, parse_mode='HTML')
                        async with session.begin():
                            stmt = (
                                insert(Subscriptions)
                                .values(
                                    user_id=i,
                                    map_id=email_id,
                                    municipality_name=response,
                                    subscribed_at=dt.now()
                                )
                            ).on_conflict_do_nothing()
                            await session.execute(stmt)
                            
                        await session.commit()

                    except SQLAlchemyError as db_err:
                        logging.error(
                            f'Ошибка базы данных при обработке пользователя {i}: {db_err}')
                        await session.rollback()
                    except Exception as e:
                        logging.error(
                            f'Ошибка при отправке пользователю {i}: {str(e)}')


@main_router.message(Command('check_email'))
async def check_email(message: Message, state: FSMContext):
    await fetch_and_save_files()
