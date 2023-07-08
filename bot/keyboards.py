from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_directions_keyboard() -> InlineKeyboardMarkup:
    ik: inline_keyboard.InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    ik.add(InlineKeyboardButton(text='Прикладная математика и информатика', callback_data='2'),
           InlineKeyboardButton(text='Фундаментальные информатика и информационные технологии', callback_data='7'),
           InlineKeyboardButton(text='Прикладные математика и физика', callback_data='9'),
           InlineKeyboardButton(text='Информатика и вычислительная техника', callback_data='14'),
           InlineKeyboardButton(text='Информационная безопасность автоматизированных систем', callback_data='17'),
           InlineKeyboardButton(text='Конструирование и технология электронных средств', callback_data='18'),
           InlineKeyboardButton(text='Электроника и наноэлектроника', callback_data='19'),
           InlineKeyboardButton(text='Радиоэлектронные системы и комплексы', callback_data='20'),
           InlineKeyboardButton(text='Фотоника и оптоинформатика', callback_data='21'),
           InlineKeyboardButton(text='Биотехнические системы и технологии', callback_data='22'),
           InlineKeyboardButton(text='Лазерная техника и лазерные технологии', callback_data='23')
           )
    return ik
