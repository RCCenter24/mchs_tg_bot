from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from aiogram.filters import Command
from database.models import Fires
from icecream import ic

daily_router = Router()


@daily_router.message(Command('daily'), F.chat.type == 'private')
async def handle_waiting_for_choise(message: types.Message, session: AsyncSession):

    unique_fires_query = select(func.count(distinct(Fires.fire_ext_id)))

    unique_fires_query_result = await session.execute(unique_fires_query)
    unique_fires = unique_fires_query_result.scalar_one()
    
