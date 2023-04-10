import django_filters as filters

from recipes.models import Ingredient, Recipe, User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr="iexact",
        label='Tags',
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        label='Favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping',
        label='Is in shopping list',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'author',
            'tags',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
