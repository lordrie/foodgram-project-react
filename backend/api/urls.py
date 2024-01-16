from django.urls import include, path
from .views import (UserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, SubscribeViewSet, SubscriptionViewSet)
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscriptions')
router.register('users/subscriptions',
                SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('users/subscriptions/',
         SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('api/users/<int:user_id>/subscribe/',
         SubscribeViewSet.as_view({'delete': 'destroy', 'post': 'create'}),
         name='unsubscribe'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
