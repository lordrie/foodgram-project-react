from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from .serializers import (UserSerializer, UserCreateSerializer,
                          UserSetPasswordSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeSerializer)
from .paginations import CustomLimitPaginator
from rest_framework import viewsets
from recipes.models import Tag, Ingredient, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomLimitPaginator

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        self.get_object = self.get_instance
        return self.retrieve(request)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return UserSetPasswordSerializer
        return UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    # Посмотреть потом на фронте поиск по первой букве
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomLimitPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
