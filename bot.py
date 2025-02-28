import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN
from services.db import init_db_pool
from handlers import calendar_handler

logging.basicConfig(level=logging.INFO)

# Создаём бота с использованием DefaultBotProperties для установки parse_mode
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def register_handlers(dispatcher: Dispatcher):
    from handlers import start_handler, help_handler, flight_search_handler, hot_deals_handler, profile_handler, navigation_handler,info_handler, weather_handler, attractions_handler, history_handler
    dispatcher.include_router(start_handler.router)
    dispatcher.include_router(help_handler.router)
    dispatcher.include_router(flight_search_handler.router)
    dispatcher.include_router(hot_deals_handler.router)
    dispatcher.include_router(profile_handler.router)
    dispatcher.include_router(navigation_handler.router)
    dispatcher.include_router(calendar_handler.router)
    dispatcher.include_router(info_handler.router)
    dispatcher.include_router(weather_handler.router)
    dispatcher.include_router(attractions_handler.router)
    dispatcher.include_router(history_handler.router)
async def main():
    await init_db_pool()
    register_handlers(dp)
    logging.info("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
