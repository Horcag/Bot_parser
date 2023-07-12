from aiogram import Dispatcher
from bot.data_base import sqlite_db
from bot import middleware, utils,handlers
from loguru import logger

logger.add('bot.log', level='DEBUG', rotation='10 MB', compression='zip', backtrace=True, diagnose=True)


async def on_startup(dispatcher: Dispatcher) -> None:
    middleware.setup(dispatcher)
    handlers.setup(dispatcher)
    await utils.setup_bot_commands(dispatcher)
    await sqlite_db.sql_start()


if __name__ == '__main__':
    utils.setup_logger('DEBUG', ['sqlalchemy.engine', 'aiogram.bot.api'])
    from aiogram import executor
    from loader import dp
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
