from re import compile, Pattern, match
from config_reader import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
import parser

storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(token=config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher(bot=bot, storage=storage)
snl_pattern: Pattern = compile(r'^\d{3}-\d{3}-\d{3}-\d{2}$')
HELP: str = '''
Команды бота:
/снилс - ввод своего СНИЛСа
/направления - выбор своего направления
'''
TEXT_DIRECTIONS: str = 'направление, где у вас высший приоритет. НЕ РАБОТАЕТ С ИНЫМИ ПРИОРИТЕТАМИ.'


class UserState(StatesGroup):
    SNILS: State = State()
    SELECT_DIRECTION: State = State()


async def on_startup(_):
    print('Бот запущен.')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Здравствуйте! Чтобы начать пользоваться нужно указать свой СНИЛС и направление. Напишите команду /снилс')
    await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP)
    await message.delete()


@dp.message_handler(commands=['снилс'])
async def get_snl(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Пожалуйста, отправьте свой СНИЛС в формате 123-456-789-00')
    await UserState.SNILS.set()


@dp.message_handler(commands=['направления'])
async def get_direction_list(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберите {TEXT_DIRECTIONS}',
                           reply_markup=keyboards.get_directions_keyboard())
    await UserState.SELECT_DIRECTION.set()


@dp.message_handler(state=UserState.SNILS)
async def process_snl(message: types.Message, state=FSMContext):
    snl: str = message.text.strip()  # Получаем переданный СНИЛС и удаляем лишние пробелы

    if match(snl_pattern, snl):
        await state.update_data(snl=snl)
        await message.reply(f"СНИЛС верный! Теперь выберете {TEXT_DIRECTIONS}.",
                            reply_markup=keyboards.get_directions_keyboard())
        await UserState.SELECT_DIRECTION.set()
    else:
        await message.reply("Неверный СНИЛС, попробуйте снова.")


@dp.callback_query_handler(state=UserState.SELECT_DIRECTION)
async def process_direction(callback_query: types.CallbackQuery, state: FSMContext):
    direction = callback_query.data  # Получаем выбранное направление
    await callback_query.answer()  # Отправляем подтверждение нажатия кнопки
    await callback_query.message.reply(f"Вы выбрали направление: {direction}")
    await state.finish()


def save_snl_to_database(snl: str):
    pass


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
