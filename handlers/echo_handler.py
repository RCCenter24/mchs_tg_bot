from aiogram import Router, F
from aiogram.types import Message


router = Router()




@router.message(F.animation)
async def echo_gif(message: Message):
    file_id = message.animation.file_id
    await message.reply(text=f'{file_id}')


@router.message(F.photo)
async def get_photo_id(message: Message):
    await message.reply(text=f"{message.photo[-1].file_id}")