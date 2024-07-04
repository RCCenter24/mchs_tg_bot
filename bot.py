import traceback
from zoneinfo import ZoneInfo
from aiogram import Dispatcher, Router, Bot
from aiogram.types import Message
from aiogram.fsm.storage.redis import (RedisStorage, DefaultKeyBuilder)
from config import bot_token
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler




bot = Bot(bot_token)

storage = RedisStorage.from_url("redis://localhost:6379/2")




async def on_startup():
    from email_checker import fetch_and_save_files
    from handlers import check_news
    try:
        await fetch_and_save_files()
        await check_news(Message)
    except Exception as e:
        print('Failed to initialize and load data:', str(e))
        traceback.print_exc()
        

async def main():
    
    dp = Dispatcher(storage = storage)
    
    from handlers import main_router
    from callbacks import main_router
    dp.include_router(main_router)
    
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Krasnoyarsk"))
    #scheduler.add_job(on_startup, 'cron', hour=0, minute=1)
    scheduler.add_job(on_startup, 'interval', minutes=0.2)
    scheduler.start()
    print('Бот запущен и готов к приему сообщений')

  
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())