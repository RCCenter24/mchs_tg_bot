from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message
from db_conn import connection
from icecream import ic
main_router = Router()

class Form(StatesGroup):
    default = State()
    waiting_for_number = State()



@main_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    cur = connection.cursor()   
    cur.execute("SELECT * FROM municipalities")
    all_municipalities = cur.fetchall()
    ic(all_municipalities)
    await message.answer(text = f'муниципальные образования \n{all_municipalities}')
    
    connection.commit()
    cur.close()
    connection.close()
     
     