import pandas as pd

# Исходный список списков
data = [[4, 2, 9],
        [7, 5, 3],
        [1, 8, 6],
        [3, 6, 2],
        [9, 1, 5]]

# Преобразование списка списков в DataFrame
df = pd.DataFrame(data, columns=['A', 'B', 'C'])

# Сортировка по нескольким значениям
# df = df.sort_values(by=['A', 'B', 'C'])
df.index = range(1, len(df) + 1)
# Преобразование DataFrame обратно в список списков
list_of_lists = [[i + 1] + lst for i, lst in enumerate(df.values.tolist())]

print(list_of_lists)