from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Municipalities
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from users.user_states import Form

from images import map_image


router = Router()


@router.message(Command('subscribe'), F.chat.type == 'private')
async def handle_subscribe_fires(message: types.Message, state: FSMContext, session: AsyncSession):

    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()

    builder = ReplyKeyboardBuilder()

    for _, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]
        builder.button(text=button_text)
    builder.button(text='Отмена')
    builder.adjust(1)
    keyboard_1 = builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="Выберите муниципальное образование")

    await message.answer_photo(caption='Выберите муниципальное образование',
                               reply_markup=keyboard_1, photo=map_image, parse_mode='HTML')

    await state.set_state(Form.waiting_for_munic)

    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])