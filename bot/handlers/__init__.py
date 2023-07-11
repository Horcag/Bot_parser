from aiogram import Dispatcher
from loguru import logger

from bot.handlers import user_handlers
from .user_handlers import start_command, cancel_command, help_command, get_snl, get_profile, get_direction_list, process_of_getting_snl, UserState, get_place, get_update, \
    process_cancel, direction_selection_process, confirmation_process, enter_snils


def setup(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(cancel_command, commands=['cancel'], state='*')
    dp.register_message_handler(get_snl, commands=['snils'])
    dp.register_message_handler(get_profile, commands=['profile'])
    dp.register_message_handler(get_direction_list, commands=['directions'])
    dp.register_message_handler(process_of_getting_snl, state=UserState.SNILS)
    dp.register_message_handler(get_place, commands=['place'])
    dp.register_callback_query_handler(get_update, lambda callback_query: callback_query.data == 'update_data')
    dp.register_callback_query_handler(process_cancel, lambda callback_query: callback_query.data == 'cancel', state='*')
    dp.register_callback_query_handler(direction_selection_process, state=UserState.SELECT_DIRECTION)
    dp.register_callback_query_handler(confirmation_process, state=UserState.YES_OR_NO_SELECT_DIRECTION)
    dp.register_callback_query_handler(enter_snils, lambda callback_query: callback_query.data == "enter_snl")
    logger.info('Handlers are set up.')
