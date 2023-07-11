from aiogram import Dispatcher
from bot.handlers import user_handlers
from bot.data_base import sqlite_db
from bot import middleware, utils,handlers
from loguru import logger
from bot.utils.set_bot_commands import setup_bot_commands
import logging

logger.add('bot.log', level='DEBUG', rotation='10 MB', compression='zip', backtrace=True, diagnose=True)


async def on_startup(dispatcher: Dispatcher) -> None:
    middleware.setup(dispatcher)
    handlers.setup(dispatcher)
    await utils.setup_bot_commands(dispatcher)
    await sqlite_db.sql_start()


if __name__ == '__main__':
    utils.setup_logger('DEBUG', ['sqlalchemy.engine', 'aiogram.bot.api'])
    # logging.basicConfig(level=logging.DEBUG,
    #                     format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", filename='bot.log')
    from aiogram import executor
    from loader import dp
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
