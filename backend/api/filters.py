import django_filters as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(rest_framework_filter.FilterSet):
    author = rest_framework_filter.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = rest_framework_filter.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = rest_framework_filter.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework_filter.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
