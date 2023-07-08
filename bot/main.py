from re import compile, Pattern, match
from config_reader import config
from aiogram import Bot, Dispatcher, executor, types
from keyboards import ik
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import parser

storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(token=config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher(bot=bot,
                            storage=storage)
snl_pattern: Pattern = compile(r'^\d{3}-\d{3}-\d{3}\s\d{2}$')


async def on_startup(_):
    print('Бот запущен.')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Пришлите свой СНИЛС в формате 123-456-789-00')
    await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Напишите /start, чтобы использовать бота.')
    await message.delete()


@dp.message_handler(commands=['направления'])
async def get_direction_list(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите направление, где у вас высший приоритет. НЕ РАБОТАЕТ С ИНЫМИ ПРИОРИТЕТАМИ.',
                           reply_markup=ik)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_snl(message: types.Message):
    snl: str = message.text.strip()  # Получаем переданный СНИЛС и удаляем лишние пробелы

    if match(snl_pattern, snl):
        save_snl_to_database(snl)
        await message.reply("СНИЛС верный! Он сохранен.")
    else:
        await message.reply("Неверный СНИЛС, попробуйте снова.")


def save_snl_to_database(snl: str):
    pass


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)
