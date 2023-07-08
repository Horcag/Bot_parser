from re import compile, Pattern, match
from config_reader import config
import keyboards
import parser
import typing

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import BotCommand

storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(token=config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher(bot=bot, storage=storage)
snl_pattern: Pattern = compile(r'^\d{3}-\d{3}-\d{3}-\d{2}$')
HELP: str = '''
<b>Команды</b>:
/snils - ввод своего СНИЛСа
/directions - выбор своего направления

<b>Что такое направление с наивысшим приоритетом?</b>
Это то направление, где Вы поставили 1.

<b>Что-то не работает или другие вопросы?</b>
Напишите @nikital_s
'''
TEXT_DIRECTIONS: str = 'направление, где у вас высший приоритет. <b>НЕ РАБОТАЕТ С ИНЫМИ ПРИОРИТЕТАМИ</b>'
TEXT_SNL: str = 'Пожалуйста, отправьте свой СНИЛС в формате <b>123-456-789-00</b>'


class UserState(StatesGroup):
    SNILS: State = State()
    SELECT_DIRECTION: State = State()
    YES_OR_NO_SELECT_DIRECTION: State = State()


async def setup_bot_commands(_):
    bot_commands = [
        BotCommand(command="/start", description="начало работы с ботом"),
        BotCommand(command="/snils", description="ввод своего СНИЛСа"),
        BotCommand(command="/directions", description="выбор своего направления"),
        BotCommand(command="/help", description="помощь")
    ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Здравствуйте! Чтобы начать пользоваться ботом нужно указать свой <b>СНИЛС</b> и <b>направление</b>.',
                           reply_markup=keyboards.command_snl(),
                           parse_mode='HTML')
    # await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP,
                           parse_mode='HTML')
    # await message.delete()


@dp.message_handler(commands=['snils'])
async def get_snl(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=TEXT_SNL,
                           reply_markup=keyboards.command_cancel(),
                           parse_mode='HTML')
    await UserState.SNILS.set()


@dp.message_handler(commands=['directions'])
async def get_direction_list(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберите {TEXT_DIRECTIONS}',
                           reply_markup=keyboards.get_directions_keyboard(),
                           parse_mode='HTML')
    await UserState.SELECT_DIRECTION.set()


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'cancel', state='*')
async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.reset_state(with_data=False)


@dp.message_handler(state=UserState.SNILS)
async def process_of_getting_snl(message: types.Message, state=FSMContext) -> None:
    snl: str = message.text.strip()  # Получаем переданный СНИЛС и удаляем лишние пробелы

    if match(snl_pattern, snl):
        async with state.proxy() as data:
            print(data)
            data['snl'] = snl
            print(data)
        if data.get('direction') is None:
            await message.answer(text=f'СНИЛС введен корректно! Теперь выберете {TEXT_DIRECTIONS}.',
                                 reply_markup=keyboards.get_directions_keyboard(),
                                 parse_mode='HTML')
            await UserState.SELECT_DIRECTION.set()
        else:
            await message.answer(text=f'СНИЛС сохранен!')
            await state.reset_state(with_data=False)
    else:
        await message.answer('Неверный СНИЛС, попробуйте снова.')


@dp.callback_query_handler(state=UserState.SELECT_DIRECTION)
async def destination_selection_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    direction = callback_query.data  # Получаем выбранное направление
    await callback_query.answer()  # Отправляем подтверждение нажатия кнопки
    async with state.proxy() as data:
        print(data)
        data['direction'] = keyboards.all_directions_dictionary[direction]
        print(data)
    await callback_query.message.edit_text(text=f'Вы выбрали направление: <b>{keyboards.all_directions_dictionary[direction]}</b>',
                                           reply_markup=keyboards.confirmation_of_selection(),
                                           parse_mode='HTML')
    await UserState.YES_OR_NO_SELECT_DIRECTION.set()


@dp.callback_query_handler(state=UserState.YES_OR_NO_SELECT_DIRECTION)
async def confirmation_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    answer = callback_query.data
    await callback_query.answer()
    match answer:
        case 'no':
            await callback_query.message.edit_text(text=f'Выберите {TEXT_DIRECTIONS}',
                                                   reply_markup=keyboards.get_directions_keyboard(),
                                                   parse_mode='HTML')
            await UserState.SELECT_DIRECTION.set()
        case 'yes':
            await callback_query.message.edit_text('Направление сохранено!')
            await state.reset_state(with_data=False)
        case _:
            raise 'Неизвестная команда'


@dp.callback_query_handler(lambda callback_query: callback_query.data == "enter_snl")
async def enter_snils(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text(text=TEXT_SNL,
                                           reply_markup=keyboards.command_cancel(),
                                           parse_mode='HTML')
    await UserState.SNILS.set()


def save_snl_to_database(snl: str):
    pass


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=setup_bot_commands)
