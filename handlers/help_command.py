from aiogram import F, Router, types
from aiogram.filters import Command




router = Router()

@router.message(Command('help'), F.chat.type == 'private')
async def handle_help(message: types.Message):
    response = ('Основные команды:\n\n'
                'выбрать муниципальное образований /subscribe \n'
                'подписаться на все муниципальные обазования /subscribe_all \n'
                'отказаться от всех подписок /cancel_subscriptions \n'
                'посмотреть мои подписки /my_subscriptions\n'
                'обратиться в техническую поддержку /support')
    await message.answer(response, parse_mode='HTML')