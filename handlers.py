import asyncio
from glob import glob
import imaplib
import os
from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message
import pandas as pd
from config import EMAIL, PASSWORD, SAVE_DIR
from db_conn import connection
from icecream import ic
from bot import bot


import aioimaplib
import ssl
from aioimaplib import IMAP4_SSL
from email import message_from_bytes
from email.header import decode_header

from email_checker import fetch_and_save_files



main_router = Router()


class Form(StatesGroup):
    waiting_for_munic = State()


@main_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    query = f"INSERT INTO users (user_id, user_name, last_name, username, joined_at) VALUES ({user_id}, '{first_name}', '{last_name}', '{username}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"
    await state.clear()
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    cur.close()

    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Выбрать муниципальное образование', callback_data='choise_munic')]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    await message.answer(text=f'Это бот по инцидентам МЧС\nЧтобы выбрать муниципальное образование нажмите'
                         'на кнопку ниже или команду /subscribe', reply_markup=markup)



@main_router.message(Command('subscribe'))
async def handle_waiting_for_choise(message: types.Message, state: FSMContext):
    cur = connection.cursor()
    cur.execute("SELECT map_id, municipality_name FROM municipalities ORDER BY municipality_name ASC")
    all_municipalities = cur.fetchall()
    
    builder = ReplyKeyboardBuilder()
    
    for index, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]  # Используем первое значение из кортежа, т.е. само имя муниципалитета
        builder.button(text=button_text)
    builder.button(text='Отмена')
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(text='Выберите муниципальное образование', reply_markup=keyboard_1)
    await state.set_state(Form.waiting_for_munic)
    
    # Сохраняем все муниципалитеты в состоянии для дальнейшей проверки
    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])
    
    
    cur.close()
    


@main_router.message(StateFilter(Form.waiting_for_munic))
async def subscribe(message: types.Message, state: FSMContext):
    selected_mun = message.text
    user_id = message.from_user.id
    
    data = await state.get_data()
    if selected_mun == "Отмена":
        await state.clear()
        await message.answer('Вы вернулись в главное меню')
        return
    all_municipalities = data.get('all_municipalities', [])
    
   
    
    
    if selected_mun in all_municipalities:
        cur = connection.cursor()
        
        
        check_query = f"SELECT 1 FROM subscriptions WHERE user_id = {user_id} AND municipality_name = '{selected_mun}' LIMIT 1"
        cur.execute(check_query)
        subscription_exists = cur.fetchone()
        
        if subscription_exists:
            await message.answer('Вы уже подписаны на это муниципальное образование.')
        else:

            insert_query = f"""
            INSERT INTO subscriptions (user_id, map_id, municipality_name, subscribed_at)
            SELECT {user_id}, m.map_id, '{selected_mun}', CURRENT_TIMESTAMP
            FROM municipalities m
            WHERE m.municipality_name = '{selected_mun}'
            ON CONFLICT DO NOTHING;
            """

            
            
            cur.execute(insert_query)
            connection.commit()

            
            query_get_subs = f"SELECT municipality_name FROM subscriptions WHERE user_id = {user_id}"
            cur.execute(query_get_subs)
            all_cathegories = cur.fetchall()

            municipalities = [item[0] for item in all_cathegories]

            message_text = "Подписка прошла успешно 🙂\n\n<b>Ваши подписки</b>\n" + "\n".join(municipalities)

            await message.answer(message_text, parse_mode='HTML')
        
        cur.close()
        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')


@main_router.message(Command('my_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext):

    await state.clear()
    user_id = message.from_user.id

    query_get_subs = f"SELECT municipality_name FROM subscriptions WHERE user_id = {user_id}"
    cur = connection.cursor()
    cur.execute(query_get_subs)
    all_cathegories = cur.fetchall()

    municipalities = [item[0] for item in all_cathegories]

    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    connection.commit()
    cur.close()

    await message.answer(message_text, parse_mode='HTML')




@main_router.message(Command('cancel_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    query = f"DELETE FROM subscriptions WHERE user_id = {user_id}"
    
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    cur.close()
    await message.answer('Вы отписались от всего😕')
    
    
@main_router.message(Command('check_news'))
async def check_news(message: Message):
    saved_files, subject, content, email_id = await fetch_and_save_files()
    print(f'email id в чек ньюс {email_id}')
    file_path = glob('saved_files/*инамика*.xlsx')
    file_path.sort(key=os.path.getmtime, reverse=True)
    latest_file_path = file_path[0]
    ic(latest_file_path)
   # cur = connection.cursor()
    df = pd.read_excel(latest_file_path)
    
    
    check_query = f"SELECT * FROM subscriptions"
   # cur.execute(check_query)
    #subscription_exists = cur.fetchall()
    df_2 = pd.read_sql_query(con=connection, sql=check_query)
    
    
    result_df = df.merge(df_2, left_on='ID Карты', right_on='map_id')
    cur = connection.cursor()
    print(f'email_id в check_news {email_id}')
    check_query = f"SELECT user_id FROM messages WHERE message_id = '{email_id}'"
    ic(check_query)
    cur.execute(check_query)
    msg_already_sent = cur.fetchall()
    ic(msg_already_sent)
    
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
                    
                    for _, row in fires.iterrows():
                        response += f"Пожар в {row['Город']} возникший {row['Дата возникновения пожара']} статус {row['Статус']}.\n"
                    
                await bot.send_message(chat_id=user_id, text=response, parse_mode='HTML')
                query = f"INSERT INTO messages (user_id, message_id, message_text, date_of_sending) VALUES ({user_id}, '{email_id}', '{response}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"
                ic(query)
                cur = connection.cursor()
                cur.execute(query)
                connection.commit()
                cur.close()
            
    



@main_router.message(Command('check_email'))
async def check_email(message: Message, state: FSMContext):
    await fetch_and_save_files()