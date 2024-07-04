from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message
from handlers import Form
from icecream import ic
from db_conn import connection



from handlers import main_router

@main_router.callback_query(F.data == 'choise_munic')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext):
    
    cur = connection.cursor()
    cur.execute("SELECT map_id, municipality_name FROM municipalities ORDER BY municipality_name ASC")
    all_municipalities = cur.fetchall()
    
    builder = ReplyKeyboardBuilder()
    
    for index, mun in enumerate(all_municipalities, start=1):
        button_text = mun[1]  # Используем первое значение из кортежа, т.е. само имя муниципалитета
        builder.button(text=button_text)
    
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.answer(text='Выберите муниципальное образование', reply_markup=keyboard_1)
    await state.set_state(Form.waiting_for_munic)
    
    # Сохраняем все муниципалитеты в состоянии для дальнейшей проверки
    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])
    
    
    cur.close()