from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# from users.user_states import Form
from config import admin_group_chat_id
from sqlalchemy.ext.asyncio import AsyncSession

from support.supported_media import SupportedMediaFilter
from aiogram.types import Message

from handlers.dialog_subscribe import MySG

from icecream import ic

router = Router()



@router.message(F.text, StateFilter(MySG.support))
async def handle_report(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    ic(message)
    await bot.send_message(chat_id = admin_group_chat_id, text = message.html_text + f"\n\n#id{message.from_user.id}", parse_mode="HTML")
    await state.clear()
    await message.answer('Ваше сообщение отправлено в техническую поддержку, ожидайте ответа🙂')
    
    
@router.message(SupportedMediaFilter(), StateFilter(MySG.support))
async def supported_media(message: Message, state: FSMContext):
    ic(message)
    if message.caption and len(message.caption) > 1000:
        return await message.reply('Описание файла слишком длинное')
    else:
        await message.copy_to(chat_id= admin_group_chat_id,
            caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
            parse_mode="HTML"
        )
        await state.clear()
        await message.answer('Ваше сообщение отправлено в техническую поддержку, ожидайте ответа🙂')