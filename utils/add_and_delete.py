from typing import Optional
import logging
from datetime import datetime as dt

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert


from database.models import Subscriptions



async def delete_munsub(session_: AsyncSession, user_id, municipality_id):
    query = delete(Subscriptions).where(
        and_(
            Subscriptions.user_id == user_id,
            Subscriptions.municipality_id == municipality_id,
        )
    )
    try:
        await session_.execute(query)
        await session_.commit()
    except Exception as e:
        logging.error(e)


async def add_munsub(session_: Optional[AsyncSession], user_id, municipality_id):
    query = select(Subscriptions.municipality_id).where(
        and_(Subscriptions.user_id == user_id,
            (Subscriptions.municipality_id == municipality_id),))
    result = await session_.execute(query)
    result = result.all()
    
    if not result:
        insert_query = (
            insert(Subscriptions).values(
                user_id=user_id, municipality_id=municipality_id, date_subscribed=dt.now()
            )
        ).on_conflict_do_nothing()

        try:
            await session_.execute(insert_query)
            await session_.commit()
        except Exception as e:
            logging.error(e)
