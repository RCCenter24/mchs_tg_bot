import logging
from aiogram.types import Message

import pandas as pd
from datetime import datetime as dt

from database.models import Messages, Municipalities, Subscriptions

from utils.df_modifier import modify_dataframe
from utils.response_maker import response_maker
from utils.result_df_maker import result_df_maker

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot import bot


async def msg_sender(message: Message, session: AsyncSession, email_id):
    df_query = text("""
                    
            select f.region, f.fire_status, f.fire_num,
                f.forestry_name, f.forces_aps, f.forces_lps,
                f.city, f.distance, f.map_id, f.fire_area, f.fire_zone, f.ext_log
                , f.*
            From fires f 
            where not exists( select 1 from fires f2 Where f2.fire_ext_id = f.fire_ext_id
                                and f.date_actual<=f2.date_actual
                                and f.date_import<=f2.date_import
                                and f2.fire_status = f.fire_status and f2.forces_aps=f.forces_aps
                                and f2.forces_lps=f.forces_lps and f2.fire_area=f.fire_area
                                and f2.fire_zone=f.fire_zone);
            
            """)

    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    df_1["fire_area"] = df_1["fire_area"].map(lambda x: str(x).replace(".", ","))
    if len(df_1) < 2:
        return
    modified_df = await modify_dataframe(df_1)
    subscribers_query = select(Subscriptions.user_id, Municipalities.map_id).join(
        Municipalities, Subscriptions.municipality_id == Municipalities.municipality_id
    )
    result = await session.execute(subscribers_query)
    subscribers = result.all()
    df_subscribers = pd.DataFrame(subscribers)
    result_df = await result_df_maker(modified_df, df_subscribers)
    if not result_df.empty:
        grouped_df = result_df.groupby("user_id")
        for user_id, group in grouped_df:
            group = group.drop_duplicates(
                subset=[
                    "region",
                    "fire_status",
                    "fire_num",
                    "forestry_name",
                    "forces_aps",
                    "forces_lps",
                    "city",
                    "distance",
                    "map_id",
                    "fire_area",
                    "fire_zone",
                ]
            )
            grouped_by_municipality = group.groupby("region")
            response = await response_maker(grouped_by_municipality)
            try:
                await bot.send_message(
                    chat_id=user_id, text=response, parse_mode="HTML"
                )
                sent_message_query = (
                    insert(Messages)
                    .values(
                        user_id=user_id,
                        email_id=email_id,
                        message_text=response,
                        date_send=dt.now(),
                    )
                    .on_conflict_do_nothing()
                )
                await session.execute(sent_message_query)
                await session.commit()
            except SQLAlchemyError as db_err:
                logging.error(
                    f"Ошибка базы данных при обработке пользователя {user_id}: {db_err}"
                )
                await session.rollback()
            except Exception as e:
                logging.error(f"Ошибка при отправке пользователю {user_id}: {str(e)}")
