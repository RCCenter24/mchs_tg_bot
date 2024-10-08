from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.models import Municipalities, Subscriptions



router=Router()

@router.message(Command('subscribe_all'), F.chat.type == 'private')
async def handle_sub_to_all_munic(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id

    subscribe_query = select(Municipalities.municipality_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    municipality_ids = [item[0] for item in all_municipalities]
    
    
    user_subs = select(Subscriptions.municipality_id).where(Subscriptions.user_id == user_id)
    result = await session.execute(user_subs)
    user_subs = result.all()
    user_subs = [item[0] for item in user_subs]
    if user_subs == []:
        for munic in municipality_ids:
            query = insert(Subscriptions).values(user_id=user_id, municipality_id=munic).on_conflict_do_nothing()
            await session.execute(query)
        await session.commit()
        await message.answer('Вы подписались на все муниципальные образования')
        return
        
    to_subscribe = list(set(municipality_ids) - set(user_subs))
    if to_subscribe != []:
        for munic in to_subscribe:
            query = insert(Subscriptions).values(user_id=user_id, municipality_id=munic).on_conflict_do_nothing()
            await session.execute(query)
        await session.commit()
        await message.answer('Вы подписались на все муниципальные образования')
        return

    await message.answer('Вы уже подписаны на все муниципальные образования')
        
        
    