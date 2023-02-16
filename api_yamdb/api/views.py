from django.conf import settings
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.mixins import ModelMixinSet
from api.permissions import (
    ChangeAdminOnly, StaffOrReadOnly, AuthorOrStaffOrReadOnly
)
from api.serializers import (
    ActivationSerializer, AdminSerializer, CategorySerializer,
    CommentSerializer, GenreSerializer, ReviewsSerializer,
    SignUpSerializer, TitleCreateSerializer,
    TitleReciveSerializer, UsersSerializer
)
from auth.get_token import get_tokens_for_user
from auth.send_code import send_mail_with_code
from reviews.models import (
    Category, Genre, Review, Title, User,
)


class SignUp(APIView):
    """
    Регистрация.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
            )[settings.SIGN_UP_USER_INDEX]
        except IntegrityError:
            return Response(
                'Имя пользователя или электронная почта занята.',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.confirmation_code = send_mail_with_code(request.data)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class Activation(APIView):
    """
    Получение JWT-токена.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(
            username=serializer.validated_data['username'])
        token = get_tokens_for_user(user)
        return Response({'token': token},
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    Работа с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (ChangeAdminOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def my_profile(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ModelMixinSet):
    """
    Получить список всех категорий.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (StaffOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """
    Получить список всех жанров.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (StaffOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех произведений.
    """

    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (StaffOrReadOnly,)
    serializer_class = TitleReciveSerializer

    def get_queryset(self):
        return Title.objects.annotate(rating=Avg('reviews_title__score'))

    def get_serializer_class(self):
        """
        Переопределяем метод get_serializer_class()
        для проверки какаяоперация REST
        была использована и возвращаем серриализаторы
        для записи и чтения.
        """
        if self.action in ['list', 'retrieve']:
            return TitleReciveSerializer
        return TitleCreateSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели Отзывов.
    """

    serializer_class = ReviewsSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_title(self):
        """Получаем произведение для отзыва."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получаем queryset."""
        return self.get_title().reviews_title.all()

    def perform_create(self, serializer):
        """Переопределяем метод create."""
        serializer.save(title=self.get_title(), author=self.request.user,)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели Комментариев.
    """

    serializer_class = CommentSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_review(self):
        """Получаем отзыв для комментария."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Получаем queryset."""
        return self.get_review().comments_review.all()

    def perform_create(self, serializer):
        """Переопределяем метод create."""
        serializer.save(review=self.get_review(), author=self.request.user)
