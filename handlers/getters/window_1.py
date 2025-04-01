
from aiogram_dialog import DialogManager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Municipalities, Subscriptions







async def window1_get_data(session_: AsyncSession, dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id
    chek_query = select(Subscriptions.municipality_id).where(Subscriptions.user_id == user_id)
    check_response = await session_.execute(chek_query)
    users_subscriptions = check_response.all()
    municipality_ids = [i[0] for i in users_subscriptions]
    
    query = select(Municipalities.municipality_id).where(Municipalities.municipality_id.in_(municipality_ids))
    response = await session_.execute(query)
    municipality_ids = response.all()
    municipality_ids = [i[0] for i in municipality_ids]

    multiselect = dialog_manager.find("munsub")
    for municipality_id in municipality_ids:
        await multiselect.set_checked(municipality_id, True)
        
    return {"user_subscriptions": users_subscriptions}