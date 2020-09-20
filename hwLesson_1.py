"""
Источник: https://5ka.ru/special_offers/

Задача организовать сбор данных, необходимо иметь метод сохранения данных в .json файлы.

Результат:
Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются
в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары
исключительно соответсвующие данной категории.

Пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import requests
import json
import copy

url_cat = 'https://5ka.ru/api/v2/categories/' # Адрес, откуда будем получать данные категорий.
url_target = 'https://5ka.ru/api/v2/special_offers' # Адрес, с которого будем брать продукты по категориям.

# Словарь параметров для запросов.
main_params = {
    'records_per_page': 20,
}

# Кортеж с символами для замены в названии файла.
replaces = (',', '-', '/', '\\', '.', '"', "'", '*', '#',)

# Получаем данные по категориям.
response = requests.get(url_cat)
data = json.loads(response.text)
print(data) # Смотрим как выглядят данные. Список словарей, работать неудобно, надо преобразовать.

# Преобразовываем данные по категориям в словарь, где ключ = код категории, значение = имя категории.
cat = {}

for itm in data:
    cat[itm['parent_group_code']] = itm['parent_group_name']

print(cat) # Смотрим как выглядят данные.


# Перебираем преобразованный словарь с категориями и получаем продукты каждой категории.
for itm, values in cat.items():
    # Формируем итоговый словарь, в который будем записывать категорию и соответствующие ей продукты.
    category = {}
    category['name'] = values
    category['code'] = itm

    params = copy.copy(main_params)
    params['categories'] = itm
    response = requests.get(url_target, params=params)
    data = json.loads(response.text)

    # Формируем список словарей продуктов.
    products = []

    for itm in data['results']:
        product = {}
        product['name'] = itm['name']
        products.append(product)

    # Помещаем сптсок словарей продуктов в итоговый словарь.
    category['products'] = products

    # Формируем имя файла согласно названию категории.
    file_name = category['name']
    for itm in replaces:
        file_name = file_name.replace(itm, '')

    # Записываем итоговый словарь в файл.
    with open(f'{file_name}.json', 'w', encoding='utf-8') as f: # Если здесь убрать "utf-8", будет ошибка.
        json.dump(category, f, ensure_ascii=False)
