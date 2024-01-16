from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, SubscribeViewSet,
                    SubscriptionViewSet, TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscriptions')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('users/subscriptions/',
         SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
