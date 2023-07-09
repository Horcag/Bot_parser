from re import compile, Pattern, match

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.keyboards import inline_keyboards
from loader import bot

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


async def start_command(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Здравствуйте! Чтобы начать пользоваться ботом нужно указать свой <b>СНИЛС</b> и <b>направление</b>.',
                           reply_markup=inline_keyboards.command_snl()
                           )
    # await message.delete()


async def help_command(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP,
                           )
    # await message.delete()


async def get_snl(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=TEXT_SNL,
                           reply_markup=inline_keyboards.command_cancel(),
                           )
    await UserState.SNILS.set()


async def get_direction_list(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберите {TEXT_DIRECTIONS}',
                           reply_markup=inline_keyboards.get_directions_keyboard(),
                           )
    await UserState.SELECT_DIRECTION.set()


async def process_of_getting_snl(message: types.Message, state=FSMContext) -> None:
    snl: str = message.text.strip()  # Получаем переданный СНИЛС и удаляем лишние пробелы

    if match(snl_pattern, snl):
        async with state.proxy() as data:
            data['snl'] = snl
        if data.get('direction') is None:
            await message.answer(text=f'СНИЛС введен корректно! Теперь выберете {TEXT_DIRECTIONS}.',
                                 reply_markup=inline_keyboards.get_directions_keyboard(),
                                 )
            await UserState.SELECT_DIRECTION.set()
        else:
            await message.answer(text=f'СНИЛС сохранен!')
            await state.reset_state(with_data=False)
    else:
        await message.answer('Неверный СНИЛС, попробуйте снова.')


async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.reset_state(with_data=False)


async def direction_selection_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    direction = callback_query.data  # Получаем выбранное направление
    await callback_query.answer()  # Отправляем подтверждение нажатия кнопки
    async with state.proxy() as data:
        data['direction'] = inline_keyboards.all_directions_dictionary[direction]
    await callback_query.message.edit_text(text=f'Вы выбрали направление: <b>{inline_keyboards.all_directions_dictionary[direction]}</b>',
                                           reply_markup=inline_keyboards.confirmation_of_selection(),
                                           )
    await UserState.YES_OR_NO_SELECT_DIRECTION.set()


async def confirmation_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    answer = callback_query.data
    await callback_query.answer()
    match answer:
        case 'no':
            await callback_query.message.edit_text(text=f'Выберите {TEXT_DIRECTIONS}',
                                                   reply_markup=inline_keyboards.get_directions_keyboard(),
                                                   )
            await UserState.SELECT_DIRECTION.set()
        case 'yes':
            await callback_query.message.edit_text('Направление сохранено!')
            await state.reset_state(with_data=False)
        case _:
            raise 'Неизвестная команда'


async def enter_snils(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text(text=TEXT_SNL,
                                           reply_markup=inline_keyboards.command_cancel(),
                                           )
    await UserState.SNILS.set()


def register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(get_snl, commands=['snils'])
    dp.register_message_handler(get_direction_list, commands=['directions'])
    dp.register_message_handler(process_of_getting_snl, state=UserState.SNILS)
    dp.register_callback_query_handler(process_cancel, lambda callback_query: callback_query.data == 'cancel', state='*')
    dp.register_callback_query_handler(direction_selection_process, state=UserState.SELECT_DIRECTION)
    dp.register_callback_query_handler(confirmation_process, state=UserState.YES_OR_NO_SELECT_DIRECTION)
    dp.register_callback_query_handler(enter_snils, lambda callback_query: callback_query.data == "enter_snl")
