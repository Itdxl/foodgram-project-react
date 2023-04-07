import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "import data from ingredients.csv"

    def handle(self, *args, **kwargs):
        with open("data/ingridient.csv", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            ingredient_to_add = [Ingredient(name=row[0],
                                 measurment_unit=row[1],)
                                 for row in reader]
            Ingredient.objects.bulk_create(ingredient_to_add)
