from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import delete

from database.models import Subscriptions



router = Router()


@router.message(Command('cancel_subscriptions'), F.chat.type == 'private')
async def handle_cancel_all_fire_subs(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_id = message.from_user.id
    delete_subs = delete(Subscriptions).where(Subscriptions.user_id == user_id)
    await session.execute(delete_subs)
    await session.commit()
    await message.answer('Вы отписались от всего😕')