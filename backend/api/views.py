from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomLimitPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          RecipeUpdateSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserCreateSerializer, UserReadSerializer,
                          UserСhangePasswordSerializer)
from .services import RecipeService, ShoppingListService
from .validators import validate_subscription, validate_unsubscription

User = get_user_model()


class UserViewSet(UserViewSet):
    """Представление для модели пользователя.
    Для чтения, создания и изменения данных пользователя."""
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    pagination_class = CustomLimitPaginator

    @action(detail=False, methods=('GET',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        self.get_object = self.get_instance
        return self.retrieve(request)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return UserСhangePasswordSerializer
        return UserReadSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для подписок.
    Для просмотра подписок пользователя."""
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomLimitPaginator

    def list(self, request):
        user = request.user
        queryset = user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(viewsets.ViewSet):
    """Представление для создания и удаления подписок."""
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post', 'delete')

    def create(self, request, user_id=None):
        """Создание подписки."""
        user = request.user
        author = get_object_or_404(User, id=user_id)
        validate_subscription(user, author)
        queryset = Subscription.objects.create(author=author, user=user)
        serializer = SubscriptionSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Удаление подписки."""
        get_object_or_404(User, id=user_id)
        validate_unsubscription(request.user, user_id)
        get_object_or_404(Subscription, user=request.user,
                          author_id=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet, RecipeService):
    """Представление для модели рецепта.
    Для просматра, создания, обновления и удаления рецепта.
    Так же добавляет рецепт в избранное и список покупок"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = CustomLimitPaginator
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        elif self.action == 'partial_update':
            return RecipeUpdateSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk):
        """Метод для добавления и удаления рецептов из избранного."""
        return RecipeService.add_delete(FavoriteSerializer, request, pk)

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        """Метод для добавления и удаления рецептов из списка покупок."""
        return RecipeService.add_delete(ShoppingCartSerializer, request, pk)


class ShoppingListDownloadView(viewsets.ReadOnlyModelViewSet):
    """Представление для cкачивания списка покупок."""
    def download(self, request):
        service = ShoppingListService(request.user)
        return service.get_shopping_list()
