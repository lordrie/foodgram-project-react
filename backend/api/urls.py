from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, ShoppingListDownloadView,
                    SubscribeViewSet, SubscriptionViewSet, TagViewSet,
                    UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShoppingListDownloadView.as_view({'get': 'get'}),
         name='download_shopping_cart'),
    path('users/subscriptions/',
         SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
