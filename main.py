from aiogram import Dispatcher
from bot.handlers import user_handlers
from bot.data_base import sqlite_db


async def on_startup(dp: Dispatcher) -> None:
    await sqlite_db.sql_start()
    from bot.utils.set_bot_commands import setup_bot_commands
    await setup_bot_commands(dp)


if __name__ == '__main__':
    from aiogram import executor
    from loader import dp

    user_handlers.register_handlers(dp)
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
