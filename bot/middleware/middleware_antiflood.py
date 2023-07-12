import asyncio
from typing import Callable, Dict, Any, Awaitable, Union
from time import time
from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from loguru import logger


def rate_limit(limit: int | float, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=1, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self, target: types.Message | types.CallbackQuery):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message_or_callback"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t)
            raise CancelHandler()

    async def target_throttled(self, target: types.Message | types.CallbackQuery,
                               throttled: Throttled) -> None:
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message_or_callback"

        delta: int = throttled.rate - throttled.delta
        if isinstance(target, types.Message):
            if throttled.exceeded_count <= 2:
                await target.reply(f'Подожди {throttled.rate} секунд прежде, чем отправить новый запрос.')
            await asyncio.sleep(delta)
            thr: Throttled = await dispatcher.check_key(key)
            if thr.exceeded_count == throttled.exceeded_count:
                await target.reply('Можете повторить запрос.')
        else:
            if throttled.exceeded_count <= 2:
                await target.message.reply(f'Подожди {throttled.rate} секунд прежде, чем отправить новый запрос.')
            await asyncio.sleep(delta)
            thr: Throttled = await dispatcher.check_key(key)
            if thr.exceeded_count == throttled.exceeded_count:
                await target.message.reply('Можете повторить запрос.')
                await target.answer()

    async def on_process_message(self, message: types.Message, data: dict):
        await self.throttle(message)

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        await self.throttle(callback_query)
