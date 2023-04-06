from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from .filters import IngredientsFilter, RecipeFilter
from .models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientInRecipe
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeAllSerializer,
    AddRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from .pagination import CustomPageNumberPagination
from .permissions import AuthorOrAdmin
from .utils import download_file


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = [AllowAny, ]
    pagination_class = None


class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = IngredientSerializer
    search_fields = ['name', ]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, ]
    filter_class = IngredientsFilter


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly | AuthorOrAdmin]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeAllSerializer
        return AddRecipeSerializer

    def perform_favorite_or_shopping_cart_action(self, request, pk=None, action_type=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if action_type == "favorite":
                action_model = Favorite
            elif action_type == "shopping_cart":
                action_model = ShoppingCart
            else:
                return Response(
                    {"error": "Неправильный тип действия"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if action_model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": f"Этот рецепт уже в {action_type}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            action_object = action_model.objects.create(user=user, recipe=recipe)
            serializer = (
                FavoriteSerializer(action_object, context={"request": request})
                if action_type == "favorite"
                else ShoppingCartSerializer(action_object, context={"request": request})
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if action_type == "favorite":
                action_model = Favorite
            elif action_type == "shopping_cart":
                action_model = ShoppingCart
            else:
                return Response(
                    {"error": "Неправильный тип действия"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            action_object = get_object_or_404(action_model, user=user, recipe=recipe)
            action_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=[AuthorOrAdmin, ],
    )
    def favorite(self, request, pk=None):
        return self.perform_favorite_or_shopping_cart_action(request, pk, "favorite")

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=[AuthorOrAdmin],
    )
    def shopping_cart(self, request, pk=None):
        return self.perform_favorite_or_shopping_cart_action(request, pk, "shopping_cart")
    @action(detail=False, methods=["GET"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients_list = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return download_file(ingredients_list)
