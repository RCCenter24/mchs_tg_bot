from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder



from sqlalchemy.ext.asyncio import AsyncSession


from user_manager import UserManager
from images import main_photo



router = Router()


@router.message(CommandStart(), F.chat.type == 'private')
async def handle_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_manager = UserManager(session)
    user_data = user_manager.extract_user_data_from_message(message)
    await user_manager.add_user_if_not_exists(user_data)

    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Выбрать муниципальное образование', callback_data='choise_munic')],
        [InlineKeyboardButton(
            text='Подписаться на все обновления', callback_data='choise_all_munic')]
    ])

    builder.adjust(1)
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    caption = ("Это бот по инцидентам МЧС Красноярского края. Чтобы подписаться на одно из муниципальных "
               "образований для получения новостей воспользуйтесь командой /subscribe \n Чтобы подписаться "
               "на все обновления нажмите на команду /subscribe_all\n")

    await message.answer_photo(caption=caption, reply_markup=markup, photo=main_photo)