from aiogram.fsm.state import StatesGroup, State



class Form(StatesGroup):
    waiting_for_munic = State()
    pre_support = State()
    support = State()