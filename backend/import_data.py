import json
from recipes.models import Ingredient
from django.conf import settings

settings.configure()

# Открытие JSON-файла и чтение его содержимого
with open('ingredients.json', 'r') as file:
    json_data = json.load(file)

# Итерация по объектам в JSON-файле
for item in json_data:
    my_model = Ingredient()
    my_model.field1 = item['field1']
    my_model.field2 = item['field2']

    # Сохранение объекта в базе данных
    my_model.save()
