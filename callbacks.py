from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Municipalities, Subscriptions
from handlers import Form
from datetime import datetime as dt

from handlers import main_router
from images import map_image

from bot import bot


@main_router.callback_query(F.data == 'choise_munic')
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
    
    try:
        await query.message.edit_caption(caption='Выберите муниципальное образование')
    
    except:
        await query.message.answer_photo(caption='Выберите муниципальное образование', reply_markup=keyboard_1)
    
    
    await state.set_state(Form.waiting_for_munic)
    
    
    await state.update_data(all_municipalities=[mun[1] for mun in all_municipalities])


@main_router.callback_query(F.data == 'choise_all_munic')
async def handle_waiting_for_choise(query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = query.from_user.id
    
    subscribe_query = select(Municipalities.map_id, Municipalities.municipality_name).order_by(
        Municipalities.municipality_name.asc())
    result = await session.execute(subscribe_query)
    all_municipalities = result.all()
    map_ids = [item[0] for item in all_municipalities]
    municipality_names  = [item[1] for item in all_municipalities]
    
    subscribers_data = [
        {
            "user_id": user_id,
            "map_id": map_id,
            "municipality_name": municipality_name,
            "subscribed_at": dt.now()
        }
        for map_id, municipality_name in zip(map_ids, municipality_names)
    ]

    
    add_subscriber_query = insert(Subscriptions).values(subscribers_data).on_conflict_do_nothing()

    await session.execute(add_subscriber_query)
    await session.commit()
    
    
    await session.execute(add_subscriber_query)
    await session.commit()
    await bot.delete_message(chat_id=user_id, message_id= query.message.message_id)
    await query.message.answer('Вы подписались на все муниципальные образования')