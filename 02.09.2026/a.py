import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.width', 1200)

RATING_COLS = ['Комфорт места', 'Обсуживание на борту', 'Еда и напитки',
               'Обслуживание на земле', 'Соотношение цены и качества', 'Развлечения']
CAT_COLS = ['Страна', 'Тип самолета', 'Тип путешественника', 'Тип места',
            'Маршрут', 'Рекомендую', 'Поездка подтверждена']
DATE_COLS = ['Дата отзыва', 'Дата полета']

# ========== Блок 1. Загрузка и первичная обработка файла data.txt ==========
data = pd.read_csv('data.txt', encoding='utf-8', sep=';',
                   engine='python', on_bad_lines='warn')
ROWS_RAW = len(data)

data.columns = [' '.join(c.split()) for c in data.columns]
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data = data.replace('', np.nan)

DUPES = int(data.duplicated().sum())
data.drop_duplicates(inplace=True)
ROWS_CLEAN = len(data)

for col in ['Заголовок отзыва', 'Содержание отзыва']:
    data[col] = data[col].str.strip().fillna('(без текста)')

def parse_date(value):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()
    formats = ['%d.%m.%Y', '%d %B %Y', '%dst %B %Y',
               '%dnd %B %Y', '%drd %B %Y', '%dth %B %Y', '%B %d, %Y']
    for fmt in formats:
        try:
            return pd.to_datetime(value, format=fmt)
        except ValueError:
            continue
    return pd.NaT

for col in DATE_COLS:
    data[col] = data[col].apply(parse_date)

for col in RATING_COLS:
    data[col] = pd.to_numeric(data[col], errors='coerce')
MISSING_RATINGS = int(data[RATING_COLS].isna().sum().sum())
for col in RATING_COLS:
    data[col] = data[col].fillna(0)

for col in CAT_COLS:
    data[col] = data[col].fillna('Не указано')

data['Общий рейтинг'] = data[RATING_COLS].sum(axis=1)

# ========== Блок 2. Фильтр: оставляем только подтвержденные отзывы ==========
verified = data[data['Поездка подтверждена'] == 'Verified'].copy()
ROWS_VER = len(verified)

# Убираем время из дат, оставляем только дату
for col in DATE_COLS:
    verified[col] = verified[col].dt.date

# ========== Блок 4. Журнал обработки ==========
print('=== ЖУРНАЛ ОБРАБОТКИ ===')
print(f'Строк в исходном файле:          {ROWS_RAW}')
print(f'Удалено дубликатов:              {DUPES}')
print(f'Строк после очистки:             {ROWS_CLEAN}')
print(f'Заменено пропусков рейтингов:    {MISSING_RATINGS}')
print(f'Подтвержденных отзывов Verified: {ROWS_VER}')
print(f'Доля Verified:                   {ROWS_VER / ROWS_CLEAN:.1%}')

# ========== Блок 5. Экспорт в Excel ==========
with pd.ExcelWriter('ba_data.xlsx', engine='openpyxl') as writer:
    data.to_excel(writer, sheet_name='Все отзывы', index=False)
    verified.to_excel(writer, sheet_name='Verified', index=False)
print('Файл ba_data.xlsx сохранен.')