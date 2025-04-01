from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from sqlalchemy.ext.asyncio import AsyncSession

from utils.message_spitter import split_message





async def button1_clicked(callback: CallbackQuery, session_: AsyncSession, dialog_manager: DialogManager):
    from handlers.dialog_subscribe import MySG
    
    clicked_button = callback.data
    if clicked_button == '1':
        await dialog_manager.switch_to(MySG.window3)
        return
    
    if clicked_button == '2':
        await dialog_manager.switch_to(MySG.window2)
        return
    
    if clicked_button == '3':
        await dialog_manager.switch_to(MySG.support)

        return

    
    await dialog_manager.next()