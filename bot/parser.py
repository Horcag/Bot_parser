from re import match, compile, Pattern
from bs4 import BeautifulSoup, element
import requests
from typing import Iterator


class University:
    def __init__(self, url: str) -> None:
        self.url: str = f'https://priemsamara.ru/ratings/?pk={url}&pay=budget&filter=all'
        self.page: requests.models.Response = requests.get(self.url)
        self.soup: BeautifulSoup = BeautifulSoup(self.page.text, 'lxml')
        self.value_tables: int = int(self.soup.find('input', id='length').get('value'))  # ищем кол-во таблиц
        self.table_with_values: element.Tag = self.soup.find('table', id=f'bak_table_id{self.value_tables}')  # нужная нам таблица последняя

    def get_data(self) -> list[str]:
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

    def get_table(self, snl: str) -> list[int]:
        it: Iterator[element.Tag] = iter(self.table_with_values.find_all('tr'))  # итератор со всеми строками из таблицы
        total_number_of_places: int = int(next(it).text.split()[-1])  # забираем последнее число - кол-во заявлений
        divs: element.ResultSet = self.soup.find_all('div', class_='numb')  # данные со всеми местами - общее кол-во бюджетных мест и под квоты
        numbers: list[int] = []  # первое число кол-во бюджетных мест, а остальные места различные квоты
        students_data: list[list[str | int]] = []  # список всех людей с их данными с наивысшим приоритетом
        count: int = 1  # счетчик людей с наивысшим приоритетом
        for div in divs:
            span: element.Tag = div.find('span')
            if span:
                number: int = int(span.text.strip())
                numbers.append(number)
        for i in it:
            student_data: list[str | int] = i.text.split()
            if student_data[8] == '1':  # делаем отбор по приоритетам: нам нужен только первый
                student_data = [count] + list(map(lambda a: int(a) if a.isdigit() else a, student_data))[1:]  # для удобства преобразуем все числовые значения в 'int'
                students_data.append(student_data)
                count += 1
        for j in students_data:  # поиск нашего СНИЛСа
            if j[1] == snl:
                last_place: int = numbers[0] - sum(numbers[1:])  # кол-во бюджетных мест и индекс последнего
                if last_place <= len(students_data):  # делаем проверку, чтобы кол-во заявлений было больше, чем бюджетных мест
                    return [j[0], students_data[last_place - 1][2], total_number_of_places, last_place]
                break
        return []

    def output(self, snl: str) -> str:
        initial_value: list[int] = self.get_table(snl)

        if initial_value:
            initial_date: list[str] = self.get_data()
            result: str = f'Дата обновления - {initial_date[0]} {initial_date[1]}\n' \
                          f'Место в списке - {initial_value[0]} из {initial_value[3]} бюджетных\n' \
                          f'Минимальный проходной балл - {initial_value[1]}\n' \
                          f'Всего заявлений - {initial_value[2]}'
            return result
        return 'Бюджетные места ещё полностью не укомплектованы или иная ошибка. Сообщите о данной проблеме автору или в поддержку.'  # обработка 'last_place <= len(value)'


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
