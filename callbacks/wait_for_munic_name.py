from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Municipalities
from users.user_states import Form

from images import map_image



router = Router()

@router.callback_query(F.data == 'choise_munic')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(Municipalities.municipality_name.asc())
    
    result = await session.execute(subscribe_query)
    all_municipalities = result.all() 
    
    builder = ReplyKeyboardBuilder()
    
    for _, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]
        builder.button(text=button_text)
    builder.button(text='Отмена')
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.answer_photo(caption='Выберите муниципальное образование',
                                   reply_markup=keyboard_1, photo=map_image, parse_mode='HTML')
    
    
    await state.set_state(Form.waiting_for_munic)
    
    
    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])