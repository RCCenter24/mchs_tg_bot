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
    await state.set_state(Form.waiting_for_munic)
    cur = connection.cursor()   
    cur.execute("SELECT municipality_name FROM municipalities ORDER BY municipality_name ASC")
    all_municipalities = cur.fetchall()
    builder = ReplyKeyboardBuilder()
    
    
    for index in enumerate(all_municipalities, start=1):

        button_text = f"{index[1]}"
        
        button_text = button_text.replace("'", "").replace("(", "").replace(")", "").replace(",", "")

        builder.button(text=button_text)
    
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    
    
    await query.message.answer(text = f'Выберите муниципальное образование', reply_markup=keyboard_1)
    
    connection.commit()
    cur.close()
    #connection.close()