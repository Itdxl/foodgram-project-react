from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientInRecipe
)
from .filters import IngredientsFilter, RecipeFilter
from .permissions import AuthorOrAdmin
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeAllSerializer,
    AddRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    CustomUserSerializer,
    ShowFollowSerializer
)
from recipes.pagination import CustomPageNumberPagination
from recipes.utils import download_file

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from users.models import Follow

User = get_user_model()


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

    def perform_favorite_or_shopping_cart_action(self,
                                                 request,
                                                 pk=None, action_type=None):
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
            action_object = action_model.objects.create(user=user,
                                                        recipe=recipe)
            serializer = (
                FavoriteSerializer(action_object, context={"request": request})
                if action_type == "favorite"
                else ShoppingCartSerializer(action_object,
                                            context={"request": request})
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
            action_object = get_object_or_404(action_model, user=user,
                                              recipe=recipe)
            action_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=[AuthorOrAdmin, ],
    )
    def favorite(self, request, pk=None):
        return self.perform_favorite_or_shopping_cart_action(request, pk,
                                                             "favorite")

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=[AuthorOrAdmin],
    )
    def shopping_cart(self, request, pk=None):
        return self.perform_favorite_or_shopping_cart_action(request, pk,
                                                             "shopping_cart")

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny, ]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        author = get_object_or_404(User, pk=pk)
        user = request.user

        if author == user:
            return Response(
                {'errors': 'Вы не можете подписываться на себя'},
                status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(author=author, user=user).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)

        obj = Follow(author=author, user=user)
        obj.save()

        serializer = ShowFollowSerializer(
            author, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        try:
            subscription = get_object_or_404(Follow, user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                'Ошибка отписки',
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ShowFollowSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
