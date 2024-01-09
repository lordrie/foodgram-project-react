from django.urls import include, path
from .views import UserViewSet
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
