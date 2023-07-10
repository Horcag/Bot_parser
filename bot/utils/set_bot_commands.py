from aiogram.types import BotCommand
from aiogram import Dispatcher


async def setup_bot_commands(dp: Dispatcher):
    bot_commands = [
        BotCommand(command="/start", description="начало работы с ботом"),
        BotCommand(command="/snils", description="ввод своего СНИЛСа"),
        BotCommand(command="/directions", description="выбор своего направления"),
        BotCommand(command="/help", description="помощь"),
        BotCommand(command="/place", description="место в списке")
    ]
    await dp.bot.set_my_commands(bot_commands)