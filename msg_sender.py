import logging
import os
from aiogram.types import Message

import pandas as pd
from datetime import datetime as dt

from database.models import Messages, Subscriptions

from email_checker import fetch_and_save_files
from utils.df_converter import df_converter
from utils.df_modifier import df_mod
from utils.result_df_maker import result_df_maker

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot import bot
from glob import glob
from icecream import ic

async def msg_sender(message: Message, session: AsyncSession):

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
    sent_user_ids = [row[0]
                     for row in msg_already_sent] if msg_already_sent else []

    if not result_df.empty:
        grouped_df = result_df.groupby('user_id')
        for user_id, group in grouped_df:
            if user_id in sent_user_ids:
                continue
            else:
                response = ""
                grouped_by_municipality = group.groupby('Район')

                for municipality, fires in grouped_by_municipality:
                    response += f"\n\n\n<b>{municipality}</b>\n"
                    status_counts = fires['icon_status'].value_counts()

                    for status, count in status_counts.items():
                        response += f"{count}{status}  "

                    for idx, row in fires.iterrows():
                        response += (f"\n\n{row['icon_status']} {row['Статус']} пожар №{row['Номер пожара']} на расстоянии {row['Расстояние']} км от {row['Город']} "
                                     f"на площади {row['Площадь обнаружения пожара']} га.")
                try:
                    await bot.send_message(chat_id=user_id, text=response, parse_mode='HTML')
                    sent_message_query = insert(Messages).values(
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
