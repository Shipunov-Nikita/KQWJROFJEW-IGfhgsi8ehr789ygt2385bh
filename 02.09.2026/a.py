import sys
import pandas as pd
import chardet

sys.stdout.reconfigure(encoding='utf-8') # Чинит вывод кириллицы в консоль

with open('data.txt', 'rb') as f: # Для узнавания кодировки файла(на всякий)
    raw = f.read(100_000)          # читаем кусок файла
    result = chardet.detect(raw)
    print(result)  

data = pd.read_csv('data.txt',
                    encoding='utf-8', # Кодировка для кириллицы файла
                    sep=';', # разделитель в файле
                    engine='python', # для обработки кавычек
                    on_bad_lines='skip', # Если всё хреново лучше скипнуть
                    )

# Отменяет обрезка длинных текстов отзывов
pd.set_option('display.max_colwidth', 60) 
pd.set_option('display.width', 1000)

data.isnull().sum() # Проверка на пустые значения в колонках

# Заполняем пустые значения в колонке на самое частое значение
# data['column_name'].fillna(data['column_name'].mode()[0], inplace=True) 
# Но это один из возможных вариантов, его лучше не использовать, а заменять на 0 и т.д., либо удалять строки с пустыми значениями, если их мало и они не важны

data.drop_duplicates(inplace=True) # Удаляем дубликаты строк, если они есть

filteder_data = data[data['Поездка подтверждена'] == 'Verified'] # Фильтруем данные по колонке, оставляем только подтверждённые поездки

print(data.columns.tolist())
print(data.head())