from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram import types
from aiogram.fsm.context import FSMContext
from users.user_states import Form
from config import admin_group_chat_id
from sqlalchemy.ext.asyncio import AsyncSession

from support.supported_media import SupportedMediaFilter
from aiogram.types import Message

router = Router()



@router.message(F.text, StateFilter(Form.support))
async def handle_report(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.send_message(chat_id = admin_group_chat_id, text = message.html_text + f"\n\n#id{message.from_user.id}", parse_mode="HTML")
    await state.clear()
    await message.answer('Ваше сообщение отправлено в техническую поддержку, ожидайте ответа🙂')
    
    
@router.message(SupportedMediaFilter(), StateFilter(Form.support))
async def supported_media(message: Message, state: FSMContext):
    if message.caption and len(message.caption) > 1000:
        return await message.reply('Описание файла слишком длинное')
    else:
        await message.copy_to(chat_id= admin_group_chat_id,
            caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
            parse_mode="HTML"
        )
        await state.clear()
        await message.answer('Ваше сообщение отправлено в техническую поддержку, ожидайте ответа🙂')