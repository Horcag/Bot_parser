from aiogram.types import BotCommand
from aiogram import Dispatcher
from loguru import logger


async def setup_bot_commands(dp: Dispatcher):
    bot_commands = [
        BotCommand(command="/start", description="начало работы с ботом"),
        BotCommand(command="/snils", description="ввод СНИЛСа"),
        BotCommand(command="/directions", description="выбор направления"),
        BotCommand(command="/place", description="место в списке"),
        BotCommand(command="/profile", description="профиль"),
        BotCommand(command="/cancel", description="отмена команды"),
        BotCommand(command="/help", description="помощь")

    ]
    await dp.bot.set_my_commands(bot_commands)

    logger.info('Standard commands are set up.')
