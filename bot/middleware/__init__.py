from .middleware_antiflood import ThrottlingMiddleware
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger
from aiogram import Dispatcher


def setup(dp: Dispatcher):
    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
    logger.info('Middlewares are set up.')
