from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message
from db_conn import connection
from icecream import ic

main_router = Router()


class Form(StatesGroup):
    waiting_for_munic = State()


@main_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    query = f"INSERT INTO users (user_id, user_name, last_name, username, joined_at) VALUES ({user_id}, '{first_name}', '{last_name}', '{username}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"
    await state.clear()
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    cur.close()

    builder = InlineKeyboardBuilder()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Выбрать муниципальное образование', callback_data='choise_munic')]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    await message.answer(text=f'Это бот по инцидентам МЧС\nЧтобы выбрать муниципальное образование нажмите'
                         'на кнопку ниже или команду /subscribe', reply_markup=markup)



@main_router.message(Command('subscribe'))
async def handle_waiting_for_choise(message: types.Message, state: FSMContext):
    cur = connection.cursor()
    cur.execute("SELECT municipality_name FROM municipalities ORDER BY municipality_name ASC")
    all_municipalities = cur.fetchall()
    builder = ReplyKeyboardBuilder()
    
    for index, mun in enumerate(all_municipalities, start=1):
        button_text = mun[0]  # Используем первое значение из кортежа, т.е. само имя муниципалитета
        builder.button(text=button_text)
    
    builder.adjust(1)
    keyboard_1 = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(text='Выберите муниципальное образование', reply_markup=keyboard_1)
    await state.set_state(Form.waiting_for_munic)
    
    # Сохраняем все муниципалитеты в состоянии для дальнейшей проверки
    await state.update_data(all_municipalities=[mun[0] for mun in all_municipalities])
    
    cur.close()
    


@main_router.message(StateFilter(Form.waiting_for_munic))
async def subscribe(message: types.Message, state: FSMContext):
    selected_mun = message.text
    user_id = message.from_user.id
    
    data = await state.get_data()
    all_municipalities = data.get('all_municipalities', [])
    
    
    if selected_mun in all_municipalities:
        cur = connection.cursor()
        
        
        check_query = f"SELECT 1 FROM subscriptions WHERE user_id = {user_id} AND municipality_name = '{selected_mun}' LIMIT 1"
        cur.execute(check_query)
        subscription_exists = cur.fetchone()
        
        if subscription_exists:
            await message.answer('Вы уже подписаны на это муниципальное образование.')
        else:
            insert_query = f"INSERT INTO subscriptions (user_id, municipality_name, subscribed_at) " \
                           f"VALUES ({user_id}, '{selected_mun}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"
            cur.execute(insert_query)
            connection.commit()

            
            query_get_subs = f"SELECT municipality_name FROM subscriptions WHERE user_id = {user_id}"
            cur.execute(query_get_subs)
            all_cathegories = cur.fetchall()

            municipalities = [item[0] for item in all_cathegories]

            message_text = "Подписка прошла успешно 🙂\n\n<b>Ваши подписки</b>\n" + "\n".join(municipalities)

            await message.answer(message_text, parse_mode='HTML')
        
        cur.close()
        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')


@main_router.message(Command('my_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext):

    await state.clear()
    user_id = message.from_user.id

    query_get_subs = f"SELECT municipality_name FROM subscriptions WHERE user_id = {user_id}"
    cur = connection.cursor()
    cur.execute(query_get_subs)
    all_cathegories = cur.fetchall()

    municipalities = [item[0] for item in all_cathegories]

    message_text = "<b>Ваши подписки</b>\n" + "\n".join(municipalities)

    connection.commit()
    cur.close()

    await message.answer(message_text, parse_mode='HTML')




@main_router.message(Command('cancel_subscriptions'))
async def handle_waiting_for_choise(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    query = f"DELETE FROM subscriptions WHERE user_id = {user_id}"
    
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    cur.close()