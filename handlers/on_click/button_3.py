from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from sqlalchemy.ext.asyncio import AsyncSession





async def button3_clicked(callback: CallbackQuery, session_: AsyncSession, dialog_manager: DialogManager):
    from handlers.dialog_subscribe import MySG
    clicked_button = callback.data
    
    if clicked_button == '3':
        await dialog_manager.switch_to(MySG.window1)
        return
    
    await dialog_manager.next()