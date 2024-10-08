import logging
from zoneinfo import ZoneInfo
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from config import bot_token
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging_config import setup_logging
from logging_middleware import LoggingMiddleware
from database.db import DataBaseSession
from database.engine import session_maker
from config import interval_min
from handlers.daily_fire_report import dayly_rep_auto
from handlers import setup_routers
from users_middleware import UsersMiddleware


bot = Bot(bot_token)

storage = RedisStorage.from_url("redis://localhost:6379/2")


async def on_startup():
    from email_checker import fetch_and_save_files
    from database.engine import session_maker
    async with session_maker() as session:
        try:
            await fetch_and_save_files(session)
        except Exception as e:
            
            logging.error(f'Failed to initialize and load data:{e}', exc_info=True)
            

async def daily_report_sender():
    async with session_maker() as session:
        await dayly_rep_auto(session)

        

async def main():
    setup_logging()
    dp = Dispatcher(storage = storage)
    
    
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    router = setup_routers()
    dp.include_router(router)
    
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(UsersMiddleware())
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Krasnoyarsk"))
    scheduler.add_job(on_startup, 'interval', minutes=interval_min)
    scheduler.add_job(daily_report_sender, 'cron', hour= 9, minute=54)
    scheduler.start()
    print('Бот запущен и готов к приему сообщений')
    logging.info('--------------------Бот запущен и готов к приему сообщений------------------------------')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)
    

if __name__ == "__main__":
    asyncio.run(main())