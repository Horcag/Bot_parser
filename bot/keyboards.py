from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

all_directions_dictionary: dict[str, str] = {
    '2': 'Прикладная математика и информатика',
    '7': 'Фундаментальные информатика и информационные технологии',
    '9': 'Прикладные математика и физика',
    '14': 'Информатика и вычислительная техника',
    '17': 'Информационная безопасность автоматизированных систем',
    '18': 'Конструирование и технология электронных средств',
    '19': 'Электроника и наноэлектроника',
    '20': 'Радиоэлектронные системы и комплексы',
    '21': 'Фотоника и оптоинформатика',
    '22': 'Биотехнические системы и технологии',
    '23': 'Лазерная техника и лазерные технологии'

}

CANCEL: InlineKeyboardButton = InlineKeyboardButton(text='Отмена ❌', callback_data='cancel')


def get_directions_keyboard() -> InlineKeyboardMarkup:
    ik: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    ik.add(InlineKeyboardButton(text=all_directions_dictionary['2'], callback_data='2'),
           InlineKeyboardButton(text=all_directions_dictionary['7'], callback_data='7'),
           InlineKeyboardButton(text=all_directions_dictionary['9'], callback_data='9'),
           InlineKeyboardButton(text=all_directions_dictionary['14'], callback_data='14'),
           InlineKeyboardButton(text=all_directions_dictionary['17'], callback_data='17'),
           InlineKeyboardButton(text=all_directions_dictionary['18'], callback_data='18'),
           InlineKeyboardButton(text=all_directions_dictionary['19'], callback_data='19'),
           InlineKeyboardButton(text=all_directions_dictionary['20'], callback_data='20'),
           InlineKeyboardButton(text=all_directions_dictionary['21'], callback_data='21'),
           InlineKeyboardButton(text=all_directions_dictionary['22'], callback_data='22'),
           InlineKeyboardButton(text=all_directions_dictionary['23'], callback_data='23'),
           CANCEL
           )
    return ik


def confirmation_of_selection() -> InlineKeyboardMarkup:
    ik: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
    ik.add(InlineKeyboardButton(text='Подтвердить ✅', callback_data='yes'),
           InlineKeyboardButton(text='Отменить ❌', callback_data='no')
           )
    return ik


def command_snl() -> InlineKeyboardMarkup:
    ik: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    ik.add(InlineKeyboardButton(text='Ввести свой снилс:', callback_data='enter_snl'),
           CANCEL
           )
    return ik


def command_cancel() -> InlineKeyboardMarkup:
    ik: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    ik.add(CANCEL)
    return ik
