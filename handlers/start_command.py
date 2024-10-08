from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


from sqlalchemy.ext.asyncio import AsyncSession


from images import main_photo
from config import TEST_MSG

router = Router()


@router.message(CommandStart(), F.chat.type == "private")
async def handle_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
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
    await message.answer(TEST_MSG, parse_mode='HTML')
    caption = ("Что умеет этот бот?\n\nБот «И 1 Лесные пожары» позволяет получить общую "
               "статистическую информацию по ряду основных параметров, характеризующих "
               "текущую лесопожарную обстановку за сутки, а также незамедлительно при обнаружении пожара.")

    await message.answer_photo(caption=caption, reply_markup=markup, photo=main_photo)
