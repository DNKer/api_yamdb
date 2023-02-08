from django.urls import include, path
from rest_framework.routers import SimpleRouter

<<<<<<< HEAD

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, TitleViewSet, UsersViewSet, get_token, signup)
=======
from .views import (Activation,
                    APIUsers,
                    CategoryViewSet,
                    CommentsViewSet,
                    GenreViewSet,
                    MyProfile,
                    ReviewsViewSet,
                    SignUp,
                    TitleViewSet)
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register(
<<<<<<< HEAD
=======
    'titles',
    TitleViewSet,
    basename='titles',
)
router_v1.register(
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
    'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
<<<<<<< HEAD
    'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/'
    r'(?P<review_id>\d+)/comments',
=======
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
    CommentsViewSet,
    basename='comments',
)
router_v1.register(
<<<<<<< HEAD
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews',
)
router_v1.register(
=======
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
    'genres',
    GenreViewSet,
    basename='genres',
)
router_v1.register(
<<<<<<< HEAD
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
=======
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
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
