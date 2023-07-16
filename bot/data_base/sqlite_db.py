import sqlite3
from datetime import datetime
from sqlite3 import Cursor, Connection

from aiogram.types import Message
from aiogram.types.base import Integer
from loguru import logger

from bot.parser.parser import University
from bot.keyboards.inline_keyboards import all_directions_dictionary as dir_dict

all_directions_dictionary: dict[str, str] = {
    '2': 'PMI',
    '7': 'FIIT',
    '9': 'PMF',
    '14': 'IVT',
    '17': 'IBAS',
    '18': 'KTES',
    '19': 'EN',
    '20': 'RSK',
    '21': 'FO',
    '22': 'BST',
    '23': 'LTLT'

}
base: Connection
cur: Cursor


async def sql_start() -> None:
    global base, cur
    base = sqlite3.connect('directions.db')
    cur = base.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS time_update (data TEXT, time TEXT, data_update_time TEXT)")
    base.commit()

    flag: bool = await get_time_update_database()
    if flag:  # заходим в цикл или сработал флаг, флаг срабатывает в двух случаях - первый запуск или новые данные
        await update_database()
    else:
        logger.info('Database has not been updated.')

    base.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY , snils TEXT, direction TEXT)")
    base.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS table_status (message_id INTEGER PRIMARY KEY , sort_orig INTEGER, sort_pr INTEGER, direction TEXT, left_margin INTEGER, "
                "right_margin INTEGER)")
    base.commit()

    logger.info('Database is set up.')


async def sql_add_user(message: Message):
    cur.execute("INSERT OR IGNORE INTO user (user_id, snils, direction) VALUES(?,?,?)", (message.from_user.id, 'None', 'None'))
    base.commit()


async def get_place(snl: str, direction: str) -> str:
    direction: str = all_directions_dictionary[direction]

    cur.execute("SELECT * FROM time_update")
    date: str
    time: str
    date, time = cur.fetchall()[-1][:2]

    cur.execute(f"SELECT * FROM {direction}")
    list_students: list[tuple[str | int]] = cur.fetchall()
    students_with_highest_priority = await get_highest_priority(list_students)
    for student_data in students_with_highest_priority:
        if student_data[1] == snl:
            cur.execute(f"SELECT places FROM places WHERE direction = '{direction}'")
            values: list[int] = []
            for row in cur.fetchall():  # данные приходят в виде списка со вложенным в него кортежем
                for value in row:
                    values.extend(list(map(int, value.split())))
            last_place = values[0] - sum(values[1:])  # кол-во бюджетных мест и индекс последнего; нулевой индекс - все бюджетные места, а остальные различные квоты
            if last_place <= len(list_students):  # делаем проверку, чтобы кол-во заявлений было больше, чем бюджетных мест
                result: str = f'<i>Дата обновления</i> – <b>{date} {time}</b>\n' \
                              f'<i>Место в списке</i> – <b>{student_data[0]}</b> <i>из</i> <b>{last_place}</b> <i>бюджетных</i>\n' \
                              f'<i>Минимальный проходной балл</i> – <b>{students_with_highest_priority[last_place - 1][2]}</b>\n' \
                              f'<i>Всего заявлений</i> – <b>{len(list_students)}</b>'
                return result

    return 'Бюджетные места ещё полностью не укомплектованы или иная ошибка. Сообщите о данной проблеме автору или в поддержку.'


async def get_highest_priority(students_data: list) -> list[list[int | str]]:
    student_data_with_highest_priority: list[list[str | int]] = []  # список всех людей с НАИВЫСШИМ ПРИОРИТЕТОМ
    count: int = 1  # счетчик людей с наивысшим приоритетом
    for student_data in students_data:
        if student_data[8] == 1 and student_data[10] == 'Сданы ВИ':
            student_data_with_highest_priority.append([count, *student_data[1:]])
            count += 1
    return student_data_with_highest_priority


async def add_snl(user_id: Integer, snl: str) -> None:
    cur.execute("UPDATE user SET snils = ? WHERE user_id = ?", (snl, user_id))
    base.commit()


async def add_direction(user_id: Integer, direction: str) -> None:
    cur.execute("UPDATE user SET direction = ? WHERE user_id = ?", (direction, user_id))
    base.commit()


async def get_user_data(user_id: Integer) -> list[str, str]:
    cur.execute("SELECT snils, direction FROM user WHERE user_id = ?", (user_id,))
    result: list = cur.fetchone()

    snl: str = result[0]
    direction: str = result[1]
    return [snl, direction]


async def update_database() -> None:
    cur.execute(f"DROP TABLE IF EXISTS places")
    base.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS places (direction TEXT, places TEXT)")
    base.commit()

    for i in all_directions_dictionary:
        cur.execute(f"DROP TABLE IF EXISTS {all_directions_dictionary[i]}")
        base.commit()

        places: list[str]
        students: list[list[int | str]]
        students, places = await University(i).get_table()

        cur.execute(f"CREATE TABLE IF NOT EXISTS {all_directions_dictionary[i]} (Ordinal_number INTEGER, SNILS_or_Number_of_application PRIMARY KEY ,\
             Amount_of_points INTEGER, Mathematics INTEGER, Physics_ICT INTEGER, Russian_language INTEGER, The_amount_of_points_for_ID INTEGER, Surrender_original TEXT, \
             Priority INTEGER, Highest_priority TEXT, Status TEXT)")
        base.commit()

        cur.executemany(f"INSERT INTO {all_directions_dictionary[i]} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students)
        base.commit()

        cur.execute("INSERT INTO places VALUES (?, ?)", (all_directions_dictionary[i], " ".join(places)))
        base.commit()

    logger.info('Database has been updated.')


async def get_time_update_database() -> bool:
    date: str
    time: str
    date, time = await University('2').get_data()

    cur.execute("INSERT INTO time_update VALUES (?, ?, ?)", (date, time, datetime.now().strftime('%d.%m.%Y - %H:%M:%S')))
    base.commit()

    cur.execute("SELECT * FROM time_update")
    res: list[tuple[str, str]] = cur.fetchall()  # получаем список кортежей с датой и временем

    last_rod_data: str
    last_rod_time: str
    if len(res) > 1:
        last_row_data, last_row_time = res[-2][:2]
    else:
        last_row_data, last_row_time = "0", "0"

    flag: bool = False  # флаг для проверки, что данные новые или старые
    if date != last_row_data or time != last_row_time:
        flag = True

    return flag


async def get_table(direction: str, sort_orig: int, sort_pr: int) -> list[str]:
    cur.execute("SELECT * FROM time_update")
    date: str
    time: str
    date, time = cur.fetchall()[-1][:2]

    sql_order: str = ''

    if sort_orig and sort_pr:
        sql_order = 'Surrender_original, Priority'
    elif sort_orig:
        sql_order = 'Surrender_original'
    elif sort_pr:
        sql_order = 'Priority'
    row_number: str = f'ROW_NUMBER() OVER (ORDER BY {sql_order}) as Number'
    if not sort_orig and not sort_pr:  # если нет никаких параметров сортировки, то и сортировать не надо
        row_number = 'Ordinal_number'
    cur.execute(f'SELECT {row_number}, SNILS_or_Number_of_application, Amount_of_points, Surrender_original, Priority FROM {all_directions_dictionary[direction]}')
    text = cur.fetchall()
    title = [('№', 'СНИЛС', 'Баллы', 'Ориг', 'Пр-ет')]
    result: list[str] = [f'{dir_dict[direction]} {date} {time}', ]
    for i in title:
        nom_t, snl_t, bal_t, orig_t, pr_t = i
        nom_t = f'|{nom_t:^2}|'
        snl_t = f'{snl_t:^19}|'
        bal_t = f'{bal_t:^5}|'
        orig_t = f'{orig_t:^4}|'
        pr_t = f'{pr_t:^5}|'
        result.append(f'{nom_t}{snl_t}{bal_t}{orig_t}{pr_t}')
    for j in text:
        nom, snl, bal, orig, pr = j
        nom = f'|{nom:^4}|'
        snl = f'{snl:^14}|'
        bal = f'{bal:^8}|'
        orig = f'{orig:^5}|'
        pr = f'{pr:^9}|'
        result.append(f'{nom}{snl}{bal}{orig}{pr}')
    return result


async def create_table_status(message_id: int, direction: str, left_margin: int, right_margin: int):
    cur.execute("INSERT OR IGNORE INTO table_status VALUES(?,?,?,?,?,?)", (message_id, 0, 0, direction, left_margin, right_margin))
    base.commit()


async def get_table_status(message: Message) -> list[int, int, str, int, int]:
    cur.execute("SELECT sort_orig, sort_pr, direction, left_margin, right_margin FROM table_status WHERE message_id = ?", (message.message_id,))
    result: list = cur.fetchone()
    sort_orig: int
    sort_pr: int
    direction: str
    left_margin: int
    right_margin: int
    sort_orig, sort_pr, direction, left_margin, right_margin = result
    return [sort_orig, sort_pr, direction, left_margin, right_margin]


async def update_sort_orig_table_status(message: Message, sort_orig: int) -> None:
    cur.execute("UPDATE table_status SET sort_orig = ? WHERE message_id = ?", (sort_orig, message.message_id))
    base.commit()


async def update_sort_pr_table_status(message: Message, sort_pr: int) -> None:
    cur.execute("UPDATE table_status SET sort_pr = ? WHERE message_id = ?", (sort_pr, message.message_id))
    base.commit()


async def update_left_margin_table_status(message: Message, left_margin: int) -> None:
    cur.execute("UPDATE table_status SET left_margin = ? WHERE message_id = ?", (left_margin, message.message_id))
    base.commit()
