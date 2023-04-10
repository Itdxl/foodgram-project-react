from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Follow
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    IngredientInRecipe,
    ShoppingCart
)


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta():
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj).exists()


class RecipeAllSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=request.user).exists()


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data

    def validate_ingredients(self, data):
        ingredients_set = []
        for ingredient in data:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError('Кол-во не меньше 1.')
            else:
                ingredients_set.append(ingredient['id'])
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError('Время не меньше 1 минуты.')
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError('минимум один ингредиент')
        elif not tags_data:
            raise serializers.ValidationError('минимум один тег')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients_data:
            ingredient_model = ingredient['id']
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_model, recipe=recipe, amount=amount
            )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            ingredients_list = [
                IngredientInRecipe(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
            IngredientInRecipe.objects.bulk_create(ingredients_list)
        return instance


class CommonSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        model = self.Meta.model

        if model.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise serializers.ValidationError('Уже в списке.')

        return data


class FavoriteSerializer(CommonSerializer):
    class Meta(CommonSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(CommonSerializer):
    class Meta(CommonSerializer.Meta):
        model = ShoppingCart


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class FollowingRecipesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields

    # def get_recipes(self, obj):
    #     recipes_limit = int(self.context['request'].GET.get(
    #         'recipes_limit', 10))
    #     user = get_object_or_404(User, pk=obj.pk)
    #     recipes = Recipe.objects.filter(author=user)[:recipes_limit]

    #     return FollowingRecipesSerializers(recipes, many=True).data

    # def get_recipes_count(self, obj):
    #     user = get_object_or_404(User, pk=obj.pk)
    #     return Recipe.objects.filter(author=user).count()
