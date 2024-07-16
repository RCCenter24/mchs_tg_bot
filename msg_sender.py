import logging
import os
from aiogram.types import Message

import pandas as pd
from datetime import datetime as dt

from database.models import Fires, Messages, Municipalities, Subscriptions

from email_checker import fetch_and_save_files
from utils.df_modifier import modify_dataframe
from utils.response_maker import response_maker
from utils.result_df_maker import result_df_maker

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot import bot
from icecream import ic

async def msg_sender(message: Message, session: AsyncSession):

    email_id = await fetch_and_save_files(session)
    
    df_query = select(Fires.region, Fires.fire_status, Fires.fire_num,
                      Fires.forestry_name, Fires.forces_aps, Fires.forces_lps,
                      Fires.city, Fires.distance, Fires.map_id, Fires.fire_area, Fires.fire_zone) \
                .where(Fires.email_id == email_id)
    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    
    
    
    modified_df = await modify_dataframe(df_1)
    
    
    
     

    subscribers_query = select(Subscriptions.user_id, Municipalities.map_id) \
                    .join(Municipalities, Subscriptions.municipality_id == Municipalities.municipality_id)
    result = await session.execute(subscribers_query)
    subscribers = result.all()

    df_subscribers = pd.DataFrame(subscribers)
    result_df = await result_df_maker(modified_df, df_subscribers)
    
    check_query = select(Messages.user_id).where(
        Messages.email_id == email_id)
    check_result = await session.execute(check_query)
    msg_already_sent = check_result.all()
    sent_user_ids = [row[0] for row in msg_already_sent] if msg_already_sent else []
    if not result_df.empty:
        grouped_df = result_df.groupby('user_id')
        for user_id, group in grouped_df:
            if user_id in sent_user_ids:
                continue
            else:
                grouped_by_municipality = group.groupby('region')
                response = await response_maker(grouped_by_municipality)                
                try:
                    await bot.send_message(chat_id=user_id, text=response, parse_mode='HTML')
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
                    logging.error(
                        f'Ошибка при отправке пользователю {user_id}: {str(e)}')
