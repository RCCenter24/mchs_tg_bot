import logging
from aiogram.filters import Command
from aiogram import Bot, Router, F
from aiogram.types import Message

import pandas as pd
from datetime import timedelta, datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from database.models import Users
from images import daily_rep_animation



router = Router()

def get_fire_count_word(number):
    if number % 100 in [11, 12, 13, 14]:
        return "лесных пожаров"
    elif number % 10 == 1:
        return "лесной пожар"
    elif 2 <= number % 10 <= 4:
        return "лесных пожара"
    else:
        return "лесных пожаров"
    
def get_fire_count_word_wo_forest(number):
    if number % 100 in [11, 12, 13, 14]:
        return "пожаров"
    elif number % 10 == 1:
        return "пожар"
    elif 2 <= number % 10 <= 4:
        return "пожара"
    else:
        return "пожаров"



@router.message(Command('daily_rep'), F.chat.type == 'private')
async def dayly_rep(message: Message, session: AsyncSession):
    
    now = dt.now()
    response = ''
    
    yesterday_start = (now - timedelta(days=1)
                       ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = now.replace(hour=9, minute=0, second=0, microsecond=0)

    yesterday_end_lie = (now - timedelta(days=1)).replace(hour=23,
                                                          minute=59, second=59, microsecond=999)

    df_query = text(f"""
                            select   f.fire_zone
            , count(f.fire_ext_id), round(sum(f.fire_area)::numeric,1) as fire_area
        from fires f
        Where  f.ext_log <>2
            and f.date_actual between '{yesterday_start}' and '{yesterday_end}'
            and f.date_import between '{yesterday_start}' and '{yesterday_end}'
            and not exists(
                Select 1 from fires f2
                Where f.fire_id <> f2.fire_id and f2.fire_ext_id = f.fire_ext_id
                    and (f2.date_actual > f.date_actual or f2.date_import > f.date_import)
                    and f2.date_actual between '{yesterday_start}' and '{yesterday_end}'
                    and f2.date_import between '{yesterday_start}' and '{yesterday_end}'
            )
        Group by Grouping sets ( (f.fire_zone),())
        Order by f.fire_zone;
        ;
                    """)

    result = await session.execute(df_query)
    df_query_result = result.all()
    
    df_1 = pd.DataFrame(df_query_result)
    df_1 = df_1.fillna('Всего')

    yesterday_end_lie = yesterday_end_lie.strftime('%H:%M %d.%m.%Y')
    summary = df_1.query('fire_zone == "Всего"')
    if not summary.empty:
        for index, row in summary.iterrows():
            if row['count'] != 0:
                fire_word = get_fire_count_word(row['count'])

                response += (f'По состоянию на {yesterday_end_lie} на территории Красноярского края действует '
                             f'<b>{row["count"]}</b> {fire_word} на площади <b>{row["fire_area"]} га.</b>')

    acc = df_1.query('fire_zone == "АСС"')
    if not acc.empty:
        for index, row in acc.iterrows():
            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв авиазоне: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')
            
    nss = df_1.query('fire_zone == "НСС"')
    if not nss.empty:
        for index, row in nss.iterrows():

            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв наземной зоне: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')

    zk = df_1.query('fire_zone == "ЗК"')
    if not zk.empty:
        for index, row in zk.iterrows():

            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв зоне контроля: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')

    if response != '':
        await message.answer_animation(animation=daily_rep_animation, caption=response, width=50, height=100, parse_mode='HTML')
    else:
        await message.answer('Данных для ежедневного отчета нет')
        
        
        
        
        



async def dayly_rep_auto(message: Message, bot: Bot, session: AsyncSession):
   
    now = dt.now()
    response = ''
    
    yesterday_start = (now - timedelta(days=1)
                       ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = now.replace(hour=9, minute=0, second=0, microsecond=0)

    yesterday_end_lie = (now - timedelta(days=1)).replace(hour=23,
                                                          minute=59, second=59, microsecond=999)

    df_query = text(f"""
                            select   f.fire_zone
            , count(f.fire_ext_id), round(sum(f.fire_area)::numeric,1) as fire_area
        from fires f
        Where  f.ext_log <>2
            and f.date_actual between '{yesterday_start}' and '{yesterday_end}'
            and f.date_import between '{yesterday_start}' and '{yesterday_end}'
            and not exists(
                Select 1 from fires f2
                Where f.fire_id <> f2.fire_id and f2.fire_ext_id = f.fire_ext_id
                    and (f2.date_actual > f.date_actual or f2.date_import > f.date_import)
                    and f2.date_actual between '{yesterday_start}' and '{yesterday_end}'
                    and f2.date_import between '{yesterday_start}' and '{yesterday_end}'
            )
        Group by Grouping sets ( (f.fire_zone),())
        Order by f.fire_zone;
        ;
                    """)

    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    df_1 = df_1.fillna('Всего')

    yesterday_end_lie = yesterday_end_lie.strftime('%H:%M %d.%m.%Y')
    summary = df_1.query('fire_zone == "Всего"')
    if not summary.empty:
        for index, row in summary.iterrows():
            if row['count'] != 0:
                fire_word = get_fire_count_word(row['count'])

                response += (f'По состоянию на {yesterday_end_lie} на территории Красноярского края действует '
                             f'<b>{row["count"]}</b> {fire_word} на площади <b>{row["fire_area"]} га.</b>')

    acc = df_1.query('fire_zone == "АСС"')
    if not acc.empty:
        for index, row in acc.iterrows():
            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв авиазоне: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')
            
    nss = df_1.query('fire_zone == "НСС"')
    if not nss.empty:
        for index, row in nss.iterrows():

            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв наземной зоне: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')

    zk = df_1.query('fire_zone == "ЗК"')
    if not zk.empty:
        for index, row in zk.iterrows():

            fire_word = get_fire_count_word_wo_forest(row['count'])

            response += (f'\nв зоне контроля: действует <b>{row["count"]}</b> {fire_word} на площади <b>'
                         f'{row["fire_area"]} га</b>.')

    if response != '':
        users_query = select(Users.user_id)
        users_result = await session.execute(users_query)
        users_list = users_result.scalars().all()
        
        for user in users_list:
            
            try:
                await bot.send_animation(chat_id=user, animation=daily_rep_animation, caption=response, width=50, height=100, parse_mode='HTML')
            except Exception as e:
                logging.info(f'Ошибка отправки пользователю {user} ежедневного отчета {e}')
