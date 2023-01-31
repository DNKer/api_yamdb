from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet, UsersViewSet)

app_name = 'api'


router = SimpleRouter()
router.register(
    'users',
    UsersViewSet,
    basename='users',
)
router.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)
router.register(
    'titles',
    TitleViewSet,
    basename='titles',
)
router.register(
    'genres',
    GenreViewSet,
    basename='genres',
)

urlpatterns = [
    path('v1/', include(router.urls)),
]