from aiogram.filters import Command
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message

from aiogram import Router, F

from sqlalchemy import select, func, and_, text, tuple_
from sqlalchemy.orm import aliased

from database.models import Fires

from datetime import timedelta, datetime as dt

from icecream import ic

from utils.summary_creator import summary_creator
from images import daily_rep_animation

main_router = Router()


@main_router.message(Command('daily_rep'), F.chat.type == 'private')
async def manual_check_news(message: Message, session: AsyncSession):
    f2 = aliased(Fires)
    now = dt.now()
    yesterday_start = (now - timedelta(days=1)
                       ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = (now - timedelta(days=1)).replace(hour=23,
                                                      minute=59, second=59, microsecond=999999)
    subquery_condition = and_(
        Fires.fire_id != f2.fire_id,
        f2.fire_ext_id == Fires.fire_ext_id,
        f2.date_actual >= Fires.date_actual
    )
    df_query = select(
        Fires.fire_zone,
        func.count(Fires.fire_ext_id),
        func.sum(Fires.fire_area).label('fire_area')
    ).join(
        f2, subquery_condition, isouter=True
    ).filter(
        f2.fire_id.is_(None),
        Fires.ext_log != 2,
        Fires.date_actual.between(yesterday_start, yesterday_end)
    ).group_by(
        func.grouping_sets(
            tuple_(Fires.fire_zone),
            tuple_()
        )
    ).order_by(
        Fires.fire_zone
    )
    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    df_1 = df_1.fillna('Всего')
    
    

    
    ic(df_1)

    response = ''

    yesterday_end = yesterday_end.strftime('%H:%M %d.%m.%Y')
    summary = df_1.query('fire_zone == "Всего"')
    if not summary.empty:
        for index, row in summary.iterrows():
            if row['count'] != 0:
                response += (f'По состоянию на {yesterday_end} на территории Красноярского края количество действующих лесных пожаров '
                             f'<b>{row["count"]}</b> на площади <b>{row["fire_area"]} га:</b>\n\n')

    acc = df_1.query('fire_zone == "АСС"')
    if not acc.empty:
        for index, row in acc.iterrows():

            response += (f'пожаров в авиазоне - <b>{row["count"]}</b>, площадь <b>{
                         row["fire_area"]} га</b>;\n')

    zk = df_1.query('fire_zone == "ЗК"')
    if not zk.empty:
        for index, row in zk.iterrows():

            response += (f'пожаров в зоне контроля -  <b>{
                         row["count"]}</b>, площадь <b>{row["fire_area"]} га</b>.')

    if response != '':
        await message.answer_animation(animation=daily_rep_animation, caption=response, width=50, height=100, parse_mode='HTML')
    else:
        await message.answer('Данных для ежедневного отчета нет')
