from django.urls import include, path
from rest_framework.routers import SimpleRouter


from .views import (Activation, CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, SignUp, TitleViewSet, UsersViewSet)

app_name = 'api'

router_v1 = SimpleRouter()
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
router_v1.register(
    'users',
    UsersViewSet,
    basename='users',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
    path('v1/auth/token/', Activation.as_view(), name='activation')
]
