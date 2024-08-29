import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.models import Fires, Messages, Municipalities, Subscriptions
from email_checker import fetch_and_save_files
from utils.df_modifier import modify_dataframe_for_command
from utils.message_spitter import split_message
from utils.response_maker import response_maker
from utils.result_df_maker import result_df_maker


import pandas as pd
from datetime import datetime as dt


router = Router()



@router.message(Command('last_news'), F.chat.type == 'private')
async def manual_check_news(message: Message, session: AsyncSession, bot: Bot):
    email_id = await fetch_and_save_files(session)
    user_id = message.from_user.id
    df_query = select(Fires.region, Fires.fire_status, Fires.fire_num,
                      Fires.forestry_name, Fires.forces_aps, Fires.forces_lps,
                      Fires.city, Fires.distance, Fires.map_id, Fires.fire_area, Fires.fire_zone, Fires.ext_log) \
                    .where(Fires.email_id == email_id)
    result = await session.execute(df_query)
    df_query_result = result.all()
    df_1 = pd.DataFrame(df_query_result)
    if not df_1.empty:
        try:
            df_1['fire_area'] = df_1['fire_area'].map(lambda x: str(x).replace('.', ','))
        except Exception as e:
            logging.error(f'не удалось изменить точку на запятую: {e}')
            
        modified_df = await modify_dataframe_for_command(df_1)
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
    
    else:                   
        await bot.send_message(chat_id=user_id, text='На текущий момент новости о пожарной обстановке отсутствуют', parse_mode='HTML')