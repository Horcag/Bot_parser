from re import match, compile, Pattern
from bs4 import BeautifulSoup, element
import pandas as pd
import requests
from typing import Iterator


class University:
    def __init__(self, url: str) -> None:
        self.url: str = f'https://priemsamara.ru/ratings/?pk={url}&pay=budget&filter=all'
        self.page: requests.models.Response = requests.get(self.url)
        self.soup: BeautifulSoup = BeautifulSoup(self.page.text, 'lxml')
        self.value_tables: int = int(self.soup.find('input', id='length').get('value'))  # ищем кол-во таблиц
        self.table_with_values: element.Tag = self.soup.find('table', id=f'bak_table_id{self.value_tables}')  # нужная нам таблица последняя

    async def get_data(self) -> list[str]:
        data_pattern: Pattern = compile(r'(0?[1-9]|[12][0-9]|3[01]).(0?[1-9]|1[012]).(2023)')
        time_pattern: Pattern = compile(r'([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])')
        data: str = ''
        time: str = ''
        for search_date_or_time in self.soup.find_all('label', class_='mini-title'):  # делаем такой поиск, потому что может поменяться формат данных
            for date_or_time in search_date_or_time.text.split():
                if date_or_time:
                    if match(data_pattern, date_or_time):
                        data = date_or_time
                    elif match(time_pattern, date_or_time):
                        time = date_or_time
        return [data, time]

    async def get_table(self) -> list[list[list[int | str]], list[str]]:
        it: Iterator[element.Tag] = iter(self.table_with_values.find_all('tr'))  # итератор со всеми строками из таблицы
        total_number_of_places: int = int(next(it).text.split()[-1])  # забираем последнее число - кол-во заявлений
        divs: element.ResultSet = self.soup.find_all('div', class_='numb')  # данные со всеми местами - общее кол-во бюджетных мест и под квоты
        places: list[str] = []  # первое число кол-во бюджетных мест, а остальные места различные квоты
        students_data: list[list[str | int]] = []  # список всех людей с их данными
        for div in divs:
            span: element.Tag = div.find('span')
            if span:
                places.append(span.text.strip())
        for i in it:
            student_data: list[str | int] = i.get_text(separator='*', strip=True).split('*')
            student_data = list(map(lambda a: int(a) if a.isdigit() else a, student_data))  # для удобства преобразуем все числовые значения в 'int'
            students_data.append(student_data)
        df = pd.DataFrame(students_data, columns=['A', 'B', 'amount_of_points', 'mat', 'phys', 'rus', 'the_amount_of_points_for_ID', 'H', 'I', 'J', 'K', 'L'])
        df = df.sort_values(['amount_of_points', 'the_amount_of_points_for_ID', 'mat', 'phys', 'rus'], ascending=(False, True, False, False, False))
        # сорт по сумме баллов -> по доп баллам -> сорт мат, икт/физ, русский
        students_data = [[i + 1] + lst[1:] for i, lst in enumerate(df.values.tolist())]
        return [students_data, places]  # Возвращаем список со студентами и кол-вом мест на направлении


if __name__ == '__main__':
    pass
    # PMI = University('2')
    # FIIT = University(7)
    # PMF = University(9)
    # IVT = University(14)
    # IBAS = University(17)
    # KTES = University(18)
    # EN = University(19)
    # RSK = University(20)
    # FO = University(21)
    # BST = University(22)
    # LTLT = University(23)
