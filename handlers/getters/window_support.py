from aiogram_dialog import DialogManager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Municipalities, Subscriptions
from icecream import ic






async def support_window_get_data(session_: AsyncSession, dialog_manager: DialogManager, **kwargs):
   user_id = dialog_manager.event.from_user.id
   ic(user_id)
    