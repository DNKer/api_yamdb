from auth.get_token import get_tokens_for_user
from auth.send_code import send_mail_with_code
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.http import JsonResponse
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.mixins import ModelMixinSet
from api.permissions import (
    ChangeAdminOnly, IamOrReadOnly,
    StaffOrReadOnly, AuthorOrStaffOrReadOnly
)
from api.serializers import (
    ActivationSerializer, AdminSerializer, CategorySerializer,
    CommentSerializer, GenreSerializer, ReviewsSerializer,
    SignUpSerializer, TitleCreateSerializer,
    TitleReciveSerializer, UsersSerializer
)
from reviews.models import Category, Genre, Review, Title, User


class SignUp(APIView):
    """
    Регистрация.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if User.objects.filter(username=request.data.get('username')).exists():
            user = User.objects.get(username=request.data.get('username'))
            if user.email == request.data['email']:
                send_mail_with_code(request.data)
                return JsonResponse(
                    {"message": "Новый код отправлен на почту"}
                )
            return Response(
                {"message": "Неверные данные"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            send_mail_with_code(request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Activation(APIView):
    """
    Получение JWT-токена.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=request.data['username']).exists():
                user = User.objects.get(username=request.data['username'])
                token = get_tokens_for_user(user)
                return Response(token)
            return Response(
                serializer.errors,
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MyProfile(APIView):
    """
    Личный профиль.
    """

    permission_classes = (IamOrReadOnly,)

    def get(self, request):
        serializer = UsersSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        if user.is_superuser or user.role == 'admin':
            serializer = AdminSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIUsers(APIView):
    """
    UsersView для обращения по username.
    """

    queryset = User.objects.all()
    permission_classes = [ChangeAdminOnly]

    def get(self, request, username):
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=username)
            serializer = UsersSerializer(user)
            return Response(serializer.data)
        return Response(
            'Вы не авторизованы',
            status=status.HTTP_401_UNAUTHORIZED
        )

    def patch(self, request, username):
        user = User.objects.get(username=username)
        serializer = AdminSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        user = User.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для Юзера.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [ChangeAdminOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    def create(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        )

    def get_queryset(self):
        """Получаем queryset."""
        return self.get_review().comments_review.all()

    def perform_create(self, serializer):
        """Переопределяем метод create."""
        serializer.save(review=self.get_review(), author=self.request.user)
