from re import compile, Pattern, match

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.keyboards import inline_keyboards
from bot.keyboards.inline_keyboards import all_directions_dictionary as dir_dict
from loader import bot
from bot.data_base import sqlite_db

snl_pattern: Pattern = compile(r'^\d{3}-\d{3}-\d{3}-\d{2}$')
HELP: str = '''
<b>Команды</b>:
/snils – ввод своего СНИЛСа
/directions – выбор своего направления
/place – место в списке (работает только после указания СНИЛСа и направления)
/profile – показывает текущее направление и СНИЛС
/cancel – отменяет любую команду ввода


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
    await sqlite_db.sql_add_user(message)
    # await message.delete()


async def help_command(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP,
                           )
    # await message.delete()


async def cancel_command(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Вы успешно отменили выполнение команды!')
    await state.reset_state(with_data=False)


async def get_snl(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=TEXT_SNL,
                           reply_markup=inline_keyboards.command_cancel(),
                           )
    await UserState.SNILS.set()


async def get_profile(message: types.Message) -> None:
    student_snl, student_directions = await sqlite_db.get_user_data(message.from_user.id)
    text_profile: str = f"{'❌' if student_snl == 'None' else '✅'} Ваш СНИЛС – <b>{'не указан' if student_snl == 'None' else student_snl}</b>\n" \
                        f"{'❌' if student_directions == 'None' else '✅'} Ваше направление – <b>{'не указано' if student_directions == 'None' else dir_dict[student_directions]}</b>"
    await bot.send_message(chat_id=message.from_user.id,
                           text=text_profile)


async def get_direction_list(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберите {TEXT_DIRECTIONS}',
                           reply_markup=inline_keyboards.get_directions_keyboard(),
                           )
    await UserState.SELECT_DIRECTION.set()


async def get_place(message: types.Message) -> None:
    text_error: str = 'Ошибка! Вы не указали'
    res = await sqlite_db.get_user_data(message.from_user.id)
    if res[0] == 'None' and res[1] == 'None':
        await message.answer(text=f'{text_error} направление и СНИЛС.')

    elif res[0] == 'None':
        await message.answer(text=f'{text_error} СНИЛС.')
    elif res[1] == 'None':
        await message.answer(text=f'{text_error} направление.')
    else:
        snl: str
        direction: str
        snl, direction = res
        output = await sqlite_db.get_place(snl=snl, direction=direction)
        await bot.send_message(chat_id=message.from_user.id,
                               text=output,
                               reply_markup=inline_keyboards.get_update_database()
                               )


async def process_of_getting_snl(message: types.Message, state: FSMContext) -> None:
    snl: str = message.text.strip()  # Получаем переданный СНИЛС и удаляем лишние пробелы

    if match(snl_pattern, snl):
        async with state.proxy() as data:
            data['snl'] = snl
            await sqlite_db.add_snl(user_id=message.from_user.id, snl=snl)
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
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await callback_query.answer()
    await state.reset_state(with_data=False)


async def direction_selection_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    direction = callback_query.data  # Получаем выбранное направление
    async with state.proxy() as data:
        data['direction'] = direction
    await callback_query.message.edit_text(text=f'Вы выбрали направление: <b>{inline_keyboards.all_directions_dictionary[direction]}</b>',
                                           reply_markup=inline_keyboards.confirmation_of_selection(),
                                           )
    await callback_query.answer()  # Отправляем подтверждение нажатия кнопки
    await UserState.YES_OR_NO_SELECT_DIRECTION.set()


async def confirmation_process(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    answer = callback_query.data
    match answer:
        case 'no':
            await callback_query.message.edit_text(text=f'Выберите {TEXT_DIRECTIONS}',
                                                   reply_markup=inline_keyboards.get_directions_keyboard(),
                                                   )
            await UserState.SELECT_DIRECTION.set()
        case 'yes':
            await callback_query.message.edit_text('Направление сохранено!')
            async with state.proxy() as data:
                await sqlite_db.add_direction(user_id=callback_query.from_user.id, direction=data['direction'])
            await state.reset_state(with_data=False)
        case _:
            raise 'Неизвестная команда'
    await callback_query.answer()


async def enter_snils(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text(text=TEXT_SNL,
                                           reply_markup=inline_keyboards.command_cancel(),
                                           )
    await UserState.SNILS.set()


async def get_update(callback_query: types.CallbackQuery) -> None:
    res: bool = await sqlite_db.get_time_update_database()
    user_snl: str
    user_direction: str
    user_snl, user_direction = await sqlite_db.get_user_data(callback_query.from_user.id)
    if res:
        text = await sqlite_db.get_place(snl=user_snl, direction=user_direction)
        await callback_query.message.edit_text(text=text,
                                               reply_markup=inline_keyboards.get_update_database()
                                               )
        await callback_query.answer('Новые данные найдены')
    else:
        await callback_query.answer('Новые данные не найдены')

