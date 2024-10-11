from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from typing import Callable, Dict, Any, Awaitable

from user_manager import UserManager


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_data = {
            "user_id": data["event_from_user"].id,
            "first_name": data["event_from_user"].first_name,
            "last_name": data["event_from_user"].last_name,
            "username": data["event_from_user"].username,
        }
        user_manager = UserManager(data["session"])
        await user_manager.add_user_if_not_exists(user_data)
        return await handler(event, data)
