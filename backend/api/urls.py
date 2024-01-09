from django.urls import include, path
from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
