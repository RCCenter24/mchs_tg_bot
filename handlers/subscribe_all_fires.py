from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.models import Municipalities, Subscriptions


from datetime import datetime as dt
from images import map_image



router=Router()

@router.message(Command('subscribe_all'), F.chat.type == 'private')
async def handle_sub_to_all_munic(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id

    subscribe_query = select(Municipalities.municipality_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    municipality_ids = [item[0] for item in all_municipalities]
    municipality_names = [item[1] for item in all_municipalities]
    subscribers_data = [
        {
            "user_id": user_id,
            "municipality_id": municipality_ids,
            "date_subscribed": dt.now()
        }
        for municipality_ids, municipality_name in zip(municipality_ids, municipality_names)
    ]
    add_subscriber_query = insert(Subscriptions).values(
        subscribers_data).on_conflict_do_nothing()
    await session.execute(add_subscriber_query)
    await session.commit()

    await message.answer('Вы подписались на все муниципальные образования')