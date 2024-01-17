from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
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
                          UserCreateSerializer, UserSerializer,
                          UserСhangePasswordSerializer)
from .services import RecipeService
from .validators import validate_subscription, validate_unsubscription

User = get_user_model()


class UserViewSet(UserViewSet):
    """Представление для модели пользователя.
    Для чтения, создания и изменения данных пользователя."""
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
            return UserСhangePasswordSerializer
        return UserSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для подписок.
    Для просмотра подписок пользователя."""
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomLimitPaginator

    def list(self, request):
        user = request.user
        queryset = user.follower.select_related('author').all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(viewsets.ViewSet):
    """Представление для создания и удаления подписок."""
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'delete', 'head']

    def create(self, request, user_id=None):
        """Создание подписки."""
        user = request.user
        author = get_object_or_404(User, id=user_id)
        validate_subscription(user, author)
        queryset = Subscription.objects.create(author=author, user=user)
        serializer = SubscriptionSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('DELETE',), detail=True)
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
    filter_backends = [DjangoFilterBackend]
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
        if request.method == 'POST':
            return RecipeService.add(FavoriteSerializer, request.user, pk)
        if request.method == 'DELETE':
            return RecipeService.delete(Favorite, request.user, pk)

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        """Метод для добавления и удаления рецептов из списка покупок."""
        if request.method == 'POST':
            return RecipeService.add(ShoppingCartSerializer, request.user, pk)
        if request.method == 'DELETE':
            return RecipeService.delete(ShoppingCart, request.user, pk)


class ShoppingListDownloadView(viewsets.ReadOnlyModelViewSet):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)

        shopping_list = ShoppingCart.objects.filter(user=request.user)
        ingredients = {}
        for item in shopping_list:
            for recipe_ingredient in item.recipe.recipes.all():
                name = recipe_ingredient.ingredient.name
                amount = recipe_ingredient.amount
                unit = recipe_ingredient.ingredient.measurement_unit
                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {'amount': amount, 'unit': unit}

        content_lines = []
        for name, info in ingredients.items():
            line = f'{name} — {info["amount"]} {info["unit"]}'
            content_lines.append(line)
        content = "\n".join(content_lines)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment;'
        'filename="shopping_list.txt"'
        return response
