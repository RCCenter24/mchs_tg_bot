import logging
from zoneinfo import ZoneInfo
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage
from config import bot_token
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging_config import setup_logging
from logging_middleware import LoggingMiddleware
from database.db import DataBaseSession
from database.engine import session_maker
from sqlalchemy.ext.asyncio import AsyncSession

bot = Bot(bot_token)

storage = RedisStorage.from_url("redis://localhost:6379/2")




async def on_startup():
    from email_checker import fetch_and_save_files
    from handlers import check_news
    from database.engine import session_maker
    async with session_maker() as session:
        try:
            await fetch_and_save_files()
            await check_news(Message, session)
        except Exception as e:
            
            logging.error('Failed to initialize and load data:', exc_info=True)
        

async def main():
    setup_logging()
    dp = Dispatcher(storage = storage)
    
    from handlers import main_router
    from callbacks import main_router
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.message.middleware
    dp.include_router(main_router)
    dp.message.middleware(LoggingMiddleware())
    
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Krasnoyarsk"))
    #scheduler.add_job(on_startup, 'cron', hour=0, minute=1)
    scheduler.add_job(on_startup, 'interval', minutes=1)
    scheduler.start()
    print('Бот запущен и готов к приему сообщений')

  
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())