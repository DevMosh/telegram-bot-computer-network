
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from main import router
from database import create_connection, create_tables  # Импортируйте нужные функции

bot = Bot(token='7200342001:AAGF_FhnhQv_9KKNuWbCCKI9PGCc6D7l2ZI', default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()

from database import create_connection, create_tables

conn = create_connection()
create_tables(conn)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
