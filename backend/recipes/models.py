from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        unique=True,
        max_length=100)
    slug = models.SlugField(
        verbose_name='Слаг тега',
        unique=True,
        max_length=100)
    color = models.CharField(
        verbose_name='Цвет тега',
        unique=True,
        max_length=7)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100

    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=100
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        # verbose_name='Изоображение',
        # upload_to='recipes/'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=100
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInResipe',
        verbose_name='Ингредиенты в рецепте',
        related_name="recipes"
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsInRecipe',
        verbose_name='Теги для рецепта',
        related_name="recipes"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Приготовление не меньше 1 минуты'),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
