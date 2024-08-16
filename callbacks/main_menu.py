from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession


from images import main_photo




router = Router()



@router.callback_query(F.data == 'main_menu')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    
    caption = ("Вы вернулись в главное меню бота по инцидентам МЧС Красноярского края. Чтобы подписаться на одно из муниципальных "
               "образований для получения новостей воспользуйтесь командой /subscribe \n Чтобы подписаться "
               "на все обновления нажмите на команду /subscribe_all\n")
    await state.clear()

    await query.message.answer_photo(caption=caption, photo=main_photo)