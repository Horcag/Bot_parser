from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

ik: inline_keyboard.InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    InlineKeyboardButton(text='Прикладная математика и информатика', callback_data='2'),
    InlineKeyboardButton(text='Фундаментальные информатика и информационные технологии'),
    InlineKeyboardButton(text='Прикладные математика и физика'),
    InlineKeyboardButton(text='Информатика и вычислительная техника'),
    InlineKeyboardButton(text='Информационная безопасность автоматизированных систем'),
    InlineKeyboardButton(text='Конструирование и технология электронных средств'),
    InlineKeyboardButton(text='Электроника и наноэлектроника'),
    InlineKeyboardButton(text='Радиоэлектронные системы и комплексы'),
    InlineKeyboardButton(text='Фотоника и оптоинформатика'),
    InlineKeyboardButton(text='Биотехнические системы и технологии'),
    InlineKeyboardButton(text='Лазерная техника и лазерные технологии')
], row_width=2)
