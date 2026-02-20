import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from database import init_db
from handlers import user, admin

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    # Инициализация БД
    await init_db()
    
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    # Удаляем вебхуки, чтобы запустить поллинг (для локальной отладки)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
