from django.urls import include, path
from rest_framework.routers import SimpleRouter


from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, TitleViewSet, UsersViewSet, get_token, signup)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/'
    r'(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews',
)
router_v1.register(
    'genres',
    GenreViewSet,
    basename='genres',
)
router_v1.register(
    'users',
    UsersViewSet,
    basename='users',
)

auth_patterns = [
    path(r'auth/token/', get_token),
    path(r'auth/signup/', signup),
]

urlpatterns = [
    path(r'v1/', include(router_v1.urls)),
    path(r'v1/', include(auth_patterns)),
]

#urlpatterns = [
#    path('v1/', include(router_v1.urls)),
#    path('v1/auth/signup/', SignUp.as_view(), name='sign_up'),
#    path('v1/auth/token/', Activation.as_view(), name='activation')
#]
