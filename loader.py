from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.config_reader import config

storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(token=config.bot_token.get_secret_value(),
               parse_mode=types.ParseMode.HTML)
dp: Dispatcher = Dispatcher(bot=bot, storage=storage)


__all__ = [
    'storage',
    'bot',
    'dp'
]