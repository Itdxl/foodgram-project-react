from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from .models import (
    Ingredient,
    Tag
    )

from .serializers import (
    TagSerializer,
    IngredientSerializer
    )


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = [AllowAny, ]
    pagination_class = None


class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = IngredientSerializer
    search_fields = ["name", ]
    pagination_class = None
    # filter_backends = [DjangoFilterBackend, ]
    # filter_class = IngredientFilter
