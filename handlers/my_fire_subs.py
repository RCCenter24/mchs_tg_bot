from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database.models import Municipalities, Subscriptions

from images import main_photo
from utils.message_spitter import split_message



router=Router()




@router.message(Command('my_subscriptions'), F.chat.type == 'private')
async def handle_my_fire_subs(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id

    query_get_subs = select(Municipalities.municipality_name) \
                    .join(Subscriptions, and_(Subscriptions.municipality_id == Municipalities.municipality_id,
                                              Subscriptions.user_id == user_id))
                    
    result = await session.execute(query_get_subs)
    all_cathegories = result.all()

    municipalities = [item[0] for item in all_cathegories]

    if municipalities == []:
        response = ('У вас нет активных подписок, чтобы подписаться нажмите /subscribe '
                    'или нажмите /help если нужна помощь')
        await message.answer(response)
        return
    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    try:
        await message.answer_photo(caption=message_text, photo=main_photo, parse_mode='HTML')
    except:
        msg_parts = await split_message(message_text)
        for parts in msg_parts:
            await message.answer(parts, parse_mode='HTML')