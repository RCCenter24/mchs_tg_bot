from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from datetime import datetime as dt

from database.models import Municipalities, Subscriptions

from users.user_states import Form




router = Router()




@router.message(StateFilter(Form.waiting_for_munic), F.chat.type == 'private')
async def subscribe(message: types.Message, state: FSMContext, session: AsyncSession):
    selected_mun = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    if selected_mun == "Отмена":
        await state.clear()
        await message.answer('Вы вернулись в главное меню', reply_markup=types.ReplyKeyboardRemove())
        return

    all_municipalities = data.get('all_municipalities', [])
    if selected_mun in all_municipalities:

        subscribe_check_query = select(Subscriptions.municipality_id) \
            .join(Municipalities, Municipalities.municipality_id == Subscriptions.municipality_id) \
            .where(
                (Subscriptions.user_id == user_id) &
                (Municipalities.municipality_name == selected_mun)
            )

        result = await session.execute(subscribe_check_query)
        subscription_exists = result.first()

        if subscription_exists is not None:
            await message.answer('Вы уже подписаны на это муниципальное образование',
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            subquery = select(Municipalities.municipality_id).where(
                Municipalities.municipality_name == selected_mun).scalar_subquery()

            add_subscriber_query = insert(Subscriptions).values(
                user_id=user_id,
                municipality_id=subquery,
                date_subscribed=dt.now()
            ).on_conflict_do_nothing()

            await session.execute(add_subscriber_query)
            await session.commit()

            query_get_subs = select(Municipalities.municipality_name) \
                    .join(Subscriptions, Subscriptions.municipality_id == Municipalities.municipality_id) \
                    .where(Subscriptions.user_id == user_id)

            result = await session.execute(query_get_subs)
            all_cathegories = result.all()

            municipalities = [item[0] for item in all_cathegories]

            message_text = "Подписка прошла успешно 🙂\n\n<b>Ваши подписки</b>\n" + \
                "\n".join(municipalities)

            await message.answer(message_text, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

        await state.clear()
    else:
        await message.answer('Пожалуйста, выберите муниципальное образование из предложенных.')