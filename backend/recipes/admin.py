from django.contrib import admin

from .models import (Favorite,
                     Ingredient, Recipe, IngredientInRecipe, RecipeTag,
                     ShoppingCart, Tag)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ('name',)


class IngredientInRecipe(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0
    min_num = 1


class RecipeTagsInline(admin.TabularInline):
    model = RecipeTag


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorite')
    list_filter = ['name', 'author', 'tags']
    inlines = (IngredientInRecipe, RecipeTagsInline)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()

    exclude = ('tags',)


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


@admin.register(ShoppingCart)
class AdminShoppingList(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
