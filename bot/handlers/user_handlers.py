from re import compile, Pattern, match

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import middleware
from bot.data_base import sqlite_db
from bot.keyboards import inline_keyboards
from bot.keyboards.inline_keyboards import all_directions_dictionary as dir_dict
from loader import bot

snl_pattern: Pattern = compile(r'^\d{3}-\d{3}-\d{3}-\d{2}$')
HELP: str = '''
<b>Команды</b>:
/snils – ввод своего СНИЛСа
/directions – выбор своего направления
/place – место в списке (работает только после указания СНИЛСа и направления)
/table - показывает таблицу выбранного направления. Выбранное направление можно посмотреть в профиле
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


async def get_table(message: types.Message) -> None:
    direction: str = (await sqlite_db.get_user_data(message.from_user.id))[1]
    table: list[str] = await sqlite_db.get_table(direction=direction, sort_orig=0, sort_pr=0)

    table_string: str = '\n'.join(table[:22])
    ln = len(table) - 2  # вычитаем, потому что в первый раз выводились названия направления и колонок
    left_margin: int = 1
    right_margin: int = ln // 20 + bool(ln % 20)
    await sqlite_db.create_table_status(message_id=message.message_id + 1, direction=direction, left_margin=left_margin, right_margin=right_margin)
    await bot.send_message(chat_id=message.from_user.id,
                           text=table_string,
                           reply_markup=inline_keyboards.get_pagination(left=left_margin, right=right_margin, sort_orig=0, sort_pr=0))


async def get_direction_list(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберите {TEXT_DIRECTIONS}',
                           reply_markup=inline_keyboards.get_directions_keyboard(),
                           )
    await UserState.SELECT_DIRECTION.set()


@middleware.rate_limit(60)
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


@middleware.rate_limit(60)
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


@middleware.rate_limit(0.2)
async def process_table(callback_query: types.CallbackQuery) -> None:
    answer = callback_query.data.split('_')
    if answer[1] == 'all':
        return await callback_query.answer()
    sort_orig: int
    sort_pr: int
    direction: str
    left_margin: int
    right_margin: int
    sort_orig, sort_pr, direction, left_margin, right_margin = await sqlite_db.get_table_status(callback_query.message)
    table: list = await sqlite_db.get_table(direction, sort_orig=sort_orig, sort_pr=sort_pr)
    if answer[1] == 'right':
        if left_margin == right_margin:
            table_string: str = '\n'.join(table[:22])
            await sqlite_db.update_left_margin_table_status(callback_query.message, left_margin=1)
            await callback_query.message.edit_text(text=table_string,
                                                   reply_markup=inline_keyboards.get_pagination(1, right_margin, sort_orig=sort_orig, sort_pr=sort_pr))
        else:
            new_left_margin = left_margin + 1
            table_string = '\n'.join([table[0], table[1], *table[left_margin * 20 + 2: new_left_margin * 20 + 2]])
            await sqlite_db.update_left_margin_table_status(callback_query.message, left_margin=new_left_margin)
            await callback_query.message.edit_text(text=table_string,
                                                   reply_markup=inline_keyboards.get_pagination(new_left_margin, right_margin, sort_orig=sort_orig, sort_pr=sort_pr))
    else:
        if left_margin == 1:
            table_string: str = '\n'.join([table[0], table[1], *table[(right_margin - 2) * 20 + 2:]])
            await sqlite_db.update_left_margin_table_status(callback_query.message, left_margin=right_margin)
            await callback_query.message.edit_text(text=table_string,
                                                   reply_markup=inline_keyboards.get_pagination(right_margin, right_margin, sort_orig=sort_orig, sort_pr=sort_pr))
        else:
            new_left_margin = left_margin - 1
            table_string = '\n'.join([table[0], table[1], *table[(new_left_margin - 1) * 20 + 2: (left_margin - 1) * 20 + 2]])
            await sqlite_db.update_left_margin_table_status(callback_query.message, left_margin=new_left_margin)
            await callback_query.message.edit_text(text=table_string,
                                                   reply_markup=inline_keyboards.get_pagination(new_left_margin, right_margin, sort_orig=sort_orig, sort_pr=sort_pr))


async def process_sort_orig_or_pr(callback_query: types.CallbackQuery) -> None:
    answer = callback_query.data
    sort_orig: int
    sort_pr: int
    direction: str
    left_margin: int
    right_margin: int
    sort_orig, sort_pr, direction, left_margin, right_margin = await sqlite_db.get_table_status(callback_query.message)
    if answer == 'sort_orig':
        sort_orig = int(not sort_orig)
        await sqlite_db.update_sort_orig_table_status(callback_query.message, sort_orig=sort_orig)
    else:
        sort_pr = int(not sort_pr)
        await sqlite_db.update_sort_pr_table_status(callback_query.message, sort_pr=sort_pr)

    table: list = await sqlite_db.get_table(direction, sort_orig=sort_orig, sort_pr=sort_pr)
    table_string = '\n'.join([table[0], table[1], *table[(left_margin - 1) * 20 + 2: left_margin * 20 + 2]])
    await callback_query.message.edit_text(text=table_string,
                                           reply_markup=inline_keyboards.get_pagination(left_margin, right_margin, sort_orig=sort_orig, sort_pr=sort_pr))