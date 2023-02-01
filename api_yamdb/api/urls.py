from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet, UsersViewSet)

app_name = 'api'


router_v1 = SimpleRouter()
router_v1.register(
    'users',
    UsersViewSet,
    basename='users',
)
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles',
)
router_v1.register(
    'genres',
    GenreViewSet,
    basename='genres',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
