from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .mixins import RecipeMixin
from .paginations import CustomLimitPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          RecipeUpdateSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer,
                          UserSetPasswordSerializer)

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


class SubscriptionViewSet(generics.GenericAPIView, viewsets.ViewSet):
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
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'delete', 'head']

    def create(self, request, user_id=None):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            return Response('Нельзя подписаться на себя',
                            status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.filter(author=author, user=user)
        if subscription.exists():
            return Response('Нельзя подписаться дважды',
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Subscription.objects.create(author=author, user=user)
        serializer = SubscriptionSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        """Удаление подписки."""
        get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response('Вы не были подписаны на автора',
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Subscription, user=request.user,
                          author_id=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet, RecipeMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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
        return RecipeSerializer

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk):
        if request.method == 'POST':
            return RecipeMixin.add(FavoriteSerializer, request.user, pk)
        if request.method == 'DELETE':
            return RecipeMixin.delete(Favorite, request.user, pk)

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return RecipeMixin.add(ShoppingCartSerializer, request.user, pk)
        if request.method == 'DELETE':
            return RecipeMixin.delete(ShoppingCart, request.user, pk)
