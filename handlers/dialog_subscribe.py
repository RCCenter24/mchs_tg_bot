import operator

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Back, Group, Multiselect, Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from sqlalchemy.ext.asyncio import AsyncSession

from handlers.on_click.button_1 import button1_clicked
from handlers.on_click.button_2 import button2_clicked
from handlers.on_click.button_3 import button3_clicked


from handlers.getters.window_1 import window1_get_data
from handlers.getters.window_2 import window2_get_data
from handlers.getters.window_support import support_window_get_data


from icecream import ic

class MySG(StatesGroup):
    window1 = State()
    window2 = State()
    window3 = State()
    window4 = State()
    support = State()






router = Router()

@router.message(CommandStart(), F.chat.type == "private")
async def handle_subscribe(message: Message, session_: AsyncSession, dialog_manager: DialogManager):
    
    """"
    Хендлер для запуска диалога
    """
    
    await dialog_manager.start(MySG.window1, mode=StartMode.RESET_STACK)

        





multi1 = Multiselect(
    Format("✅ {item[0]}"),
    Format("☑️{item[0]}"),
    id="munsub",
    item_id_getter=operator.itemgetter(1),
    items="municsubscritions",
    on_click=button2_clicked
)



dialog = Dialog(
    Window(
        Format("Добро пожаловать"),
        Button(Const("Выбрать муниципальные образования"), id="1", on_click=button1_clicked),
        Button(Const("🆘Помощь"), id="2", on_click=button1_clicked),
        # Button(Const("🗞️Получить новости"), id="3", on_click=check_news),
        state=MySG.window1,
        getter=window1_get_data),
    Window(
        Format("Если нужна помощь то не звоните"),
        Button(Const("Обратиться в техподдержку"), id="3", on_click=button1_clicked),
        Back(Const("⏪Назад")),
        state=MySG.window2,
    ),
    Window(
        Format("Напишите свое обращение"),
        Back(Const("⏪Назад")),
        state=MySG.support,
        getter=support_window_get_data
    ),
    Window(
        Format("Муниципальные образования для выбора"),
        Group(Button(Const("✅подписаться на все"), id="all", on_click=button2_clicked),
              Button(Const("❌отписаться от всего"), id="noall", on_click=button2_clicked), width=2),
        Group(multi1, width=1),
        Back(Const("⏪Назад")),
        Button(Const("🆘Помощь"), id="2", on_click=button1_clicked),
        state=MySG.window3,
        getter=window2_get_data,
        markup_factory=ReplyKeyboardFactory(selective=True, resize_keyboard=True,
                                            input_field_placeholder = Const(text= 'Выберите муниципальное образование')),
    ),
    
)