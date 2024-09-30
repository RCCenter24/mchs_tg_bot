import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd

from database.models import Municipalities, Subscriptions, Users
import os
from icecream import ic





router=Router()




@router.message(Command('statistics'), F.chat.type == 'private')
async def handle_get_all_subscribers(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()


    query = select(Users.user_id, Users.first_name, Users.last_name, Users.username, Subscriptions.municipality_id, Municipalities.municipality_name) \
                    .join(Users, Users.user_id == Subscriptions.user_id).join(Municipalities, Subscriptions.municipality_id == Municipalities.municipality_id) \
                    .order_by(Users.user_id)
                    
    result = await session.execute(query)
    all_subs = result.all()
    
    df = pd.DataFrame(all_subs)
    df.drop(columns=['municipality_id'], inplace=True)
    unique_users = int(df['user_id'].nunique())
    subscribers_amount = df.shape[0]
    destination = 'var/log/tg_bot'
    if not os.path.exists(destination):
        os.makedirs(destination)
    filename = 'Подписчики.xlsx'
    filepath = os.path.join(destination, filename)
        
    
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Подписки')
    workbook = writer.book
    worksheet = writer.sheets['Подписки']
    for i, col in enumerate(df.columns):
        width = max(df[col].apply(lambda x: len(str(x))).max(), len(col))
        worksheet.set_column(i, i, width)
    writer.close()
    
    
    try:
        await message.answer_document(document=FSInputFile(filepath), caption=f'Количество пользователей: <b>{unique_users}</b>\n\nВсего подписок: <b>{subscribers_amount}</b>', parse_mode='HTML')
    except Exception as e:
        logging.info(f'Не удалось отправить файл: {e}')
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
    
    
    