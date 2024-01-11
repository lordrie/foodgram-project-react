from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from .serializers import (UserSerializer, UserCreateSerializer,
                          UserSetPasswordSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          RecipeUpdateSerializer, SubscriptionSerializer)
from .paginations import CustomLimitPaginator
from rest_framework import viewsets, status, generics
from recipes.models import Tag, Ingredient, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from users.models import Subscription

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

    def destroy(self, request, user_id=None):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        subscription = Subscription.objects.filter(author=author, user=user)
        if not subscription.exists():
            return Response('Нельзя отписаться повторно',
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
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
    # Посмотреть потом на фронте поиск по первой букве
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
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
        elif self.action in ['partial_update']:
            return RecipeUpdateSerializer
        return RecipeSerializer
