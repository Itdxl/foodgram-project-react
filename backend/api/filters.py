import django_filters as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.CharFilter(method="get_filter_by_flag")
    is_in_shopping_cart = filters.CharFilter(method='get_filter_by_flag')

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def get_filter_by_flag(self, queryset, name, value):
        user = self.request.user
        flag_field = None
        if name == 'is_favorited':
            flag_field = 'in_favorite__user'
        elif name == 'is_in_shopping_cart':
            flag_field = 'shopping_cart__user'
        if value:
            return Recipe.objects.filter(**{flag_field: user})
        return Recipe.objects.all()


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
