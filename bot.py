from aiogram import Dispatcher, Router, Bot
from aiogram.fsm.storage.redis import (RedisStorage, DefaultKeyBuilder)
from config import bot_token
import asyncio
bot = Bot(bot_token)

storage = RedisStorage.from_url("redis://localhost:6379/2")







async def main():
    
    dp = Dispatcher(storage = storage)
    from handlers import main_router
    dp.include_router(main_router)
    
    
    print('Бот запущен и готов к приему сообщений')

  
    await dp.start_polling(bot)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())