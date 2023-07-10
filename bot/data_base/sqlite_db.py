import sqlite3
import sqlite3 as sq
from sqlite3 import Cursor, Connection

from aiogram.types import Message

from bot.parser.parser import University
from aiogram.dispatcher import FSMContext

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

    cur.execute("CREATE TABLE IF NOT EXISTS time_update (data TEXT, time TEXT)")
    base.commit()

    data: str
    time: str
    data, time = University('2').get_data()

    cur.execute("INSERT INTO time_update VALUES (?,?)", (data, time))
    base.commit()

    cur.execute("SELECT * FROM time_update")
    res: list[tuple[str, str]] = cur.fetchall()  # получаем список кортежей с датой и временем

    last_rod_data: str
    last_rod_time: str
    if len(res) > 1:
        last_row_data, last_row_time = res[-2]
    else:
        last_row_data, last_row_time = "0", "0"

    flag: bool = False  # флаг для проверки, что данные новые или старые
    if data != last_row_data or time != last_row_time:
        flag = True
    if flag:  # заходим в цикл или сработал флаг, флаг срабатывает в двух случаях - первый запуск или новые данные
        cur.execute(f"DROP TABLE IF EXISTS places")
        base.commit()

        cur.execute("CREATE TABLE IF NOT EXISTS places (direction TEXT, places TEXT)")
        base.commit()

        for i in all_directions_dictionary:
            if flag:
                cur.execute(f"DROP TABLE IF EXISTS {all_directions_dictionary[i]}")
                base.commit()

            places: list[str]
            students: list[list[int | str]]
            students, places = University(i).get_table()

            cur.execute(f"CREATE TABLE IF NOT EXISTS {all_directions_dictionary[i]} (Ordinal_number INTEGER, SNILS_or_Number_of_application PRIMARY KEY ,\
             Amount_of_points INTEGER, Mathematics INTEGER, Physics_ICT INTEGER, Russian_language INTEGER, The_amount_of_points_for_ID INTEGER, Surrender_original TEXT, \
             Priority INTEGER, Highest_priority TEXT, Status TEXT)")
            base.commit()

            cur.executemany(f"INSERT INTO {all_directions_dictionary[i]} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students)
            base.commit()

            cur.execute("INSERT INTO places VALUES (?, ?)", (all_directions_dictionary[i], " ".join(places)))
            base.commit()

    base.execute("CREATE TABLE IF NOT EXISTS user (user_id PRIMARY KEY , snils TEXT, direction TEXT)")
    base.commit()

    print('Base update')


async def sql_add_user(message: Message):
    cur.execute("INSERT OR IGNORE INTO user (user_id, snils, direction) VALUES(?,?,?)", (message.from_user.id, 'None', 'None'))
    base.commit()


def get_place(snl: str, direction: str) -> str:
    direction: str = all_directions_dictionary[direction]

    cur.execute("SELECT * FROM time_update")
    data: str
    time: str
    data, time = cur.fetchall()[-1]

    cur.execute(f"SELECT * FROM {direction}")
    list_students: list[tuple[str | int]] = cur.fetchall()
    students_with_highest_priority = get_highest_priority(list_students)
    for student_data in students_with_highest_priority:
        if student_data[1] == snl:
            cur.execute(f"SELECT places FROM places WHERE direction = '{direction}'")
            values: list[int] = []
            for row in cur.fetchall():  # данные приходят в виде списка со вложенным в него кортежем
                for value in row:
                    values.extend(list(map(int, value.split())))
            last_place = values[0] - sum(values[1:])  # кол-во бюджетных мест и индекс последнего; нулевой индекс - все бюджетные места, а остальные различные квоты
            if last_place <= len(list_students):  # делаем проверку, чтобы кол-во заявлений было больше, чем бюджетных мест
                result: str = f'Дата обновления - {data} {time}\n' \
                              f'Место в списке - {student_data[0]} из {last_place} бюджетных\n' \
                              f'Минимальный проходной балл - {students_with_highest_priority[last_place - 1][2]}\n' \
                              f'Всего заявлений - {len(list_students)}'
                return result

    return 'Бюджетные места ещё полностью не укомплектованы или иная ошибка. Сообщите о данной проблеме автору или в поддержку.'


def get_highest_priority(students_data: list) -> list[list[int | str]]:
    student_data_with_highest_priority: list[list[str | int]] = []  # список всех людей с НАИВЫСШИМ ПРИОРИТЕТОМ
    count: int = 1  # счетчик людей с наивысшим приоритетом
    for student_data in students_data:
        if student_data[8] == 1 and student_data[10] == 'Сданы ВИ':
            student_data_with_highest_priority.append([count, *student_data[1:]])
            count += 1
    return student_data_with_highest_priority


async def add_snl(message: Message, snl: str):
    cur.execute("UPDATE user SET snils = ? WHERE user_id = ?", (snl, message.from_user.id))
    base.commit()


async def add_direction(message: Message, direction: str):
    cur.execute("UPDATE user SET direction = ? WHERE user_id = ?", (direction, message.chat.id))
    base.commit()


def get_snl_and_direction(message: Message) -> list[str, str]:
    user_id = message.from_user.id
    cur.execute("SELECT snils, direction FROM user WHERE user_id = ?", (user_id,))
    result: list = cur.fetchone()

    if result is not None:
        if result[0] is not None:
            snl: str = result[0]
        else:
            return []
        if result[1] is not None:
            direction: str = result[1]
        else:
            return []
        return [snl, direction]
    return []
