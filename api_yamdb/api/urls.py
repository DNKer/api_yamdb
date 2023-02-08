from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    Activation, APIUsers, CategoryViewSet,
    CommentsViewSet, GenreViewSet, MyProfile,
    ReviewsViewSet, SignUp, TitleViewSet
)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles',
)
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments',
)
router_v1.register(
    'genres',
    GenreViewSet,
    basename='genres',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews',
)

urlpatterns = [
    path('v1/users/me/', MyProfile.as_view(), name='users'),
    path('v1/users/', APIUsers.as_view()),
    path('v1/users/<slug:username>/', APIUsers.as_view()),
    path('v1/users/me/', MyProfile.as_view(), name='me'),
    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
    path('v1/auth/token/', Activation.as_view(), name='activation'),
    path('v1/', include(router_v1.urls)),
]
