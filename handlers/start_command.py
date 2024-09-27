from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


from sqlalchemy.ext.asyncio import AsyncSession


from user_manager import UserManager
from images import main_photo


router = Router()


@router.message(CommandStart(), F.chat.type == "private")
async def handle_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_manager = UserManager(session)
    user_data = user_manager.extract_user_data_from_message(message)
    await user_manager.add_user_if_not_exists(user_data)

    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выбрать муниц. образование",
                    callback_data="choise_munic",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Подписаться на все обновления",
                    callback_data="choise_all_munic",
                )
            ],
        ]
    )

    builder.adjust(1)
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    caption = ("Что умеет этот бот?\n\nБот «И 1 Лесные пожары» позволяет получить общую "
               "статистическую информацию по ряду основных параметров, характеризующих "
               "текущую лесопожарную обстановку за сутки, а также незамедлительно при обнаружении пожара.")

    await message.answer_photo(caption=caption, reply_markup=markup, photo=main_photo)
