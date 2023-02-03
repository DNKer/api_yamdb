import os
import secrets


from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView


from api.mixins import ModelMixinSet
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    NotAdminSerializer,
    ReviewsSerializer,
    SignUpSerializer,
    TitleCreateSerializer,
    TitleReciveSerializer,
    UsersSerializer,
)
from api_yamdb.settings import CONFIRMATION_DIR
from core.token import get_tokens_for_user
from reviews.models import Category, Genre, Review, Title, User


class SignUp(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request,):
        serializer = SignUpSerializer(data=request.data)
        confirmation_code = secrets.randbelow(1000000)
        if serializer.is_valid():
            email = request.data['email']
            username = request.data['username']
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения {confirmation_code}',
                'YamDB@mail.ru',
                [email],
                fail_silently=True
            )
            serializer.save()
            with open(f'{CONFIRMATION_DIR}/{username}.env', mode='w') as f:
                f.write(str(confirmation_code))

            return JsonResponse(
                {"message": "Код подтверждения отправлен на почту"}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Activation(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data['username']
        user_code = int(request.data['confirmation_code'])
        user = User.objects.get(username=username)
        path = f'{CONFIRMATION_DIR}/{username}.env'
        with open(path,) as f:
            confirmation_code = int(f.read())
            if user_code == confirmation_code:
                token = get_tokens_for_user(user)
                f.close()
                os.remove(path)
                return JsonResponse(token)
            raise ValidationError('Неверный код')


class UsersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели User.
    Администратор имеет полные права доступа.
    Пользователь может просматривать и редактировать свой аккаунт.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (permissions.AllowAny,)  # IsAdminUser
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @api_view(['GET', 'PATCH'])
    def get_current_user_info(self, request):
        """Просмотр и изменение своего аккаунта."""
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class CategoryViewSet(ModelMixinSet):
    """
    Получить список всех категорий.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = (,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """
    Получить список всех жанров.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes = (,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех произведений.
    """

    queryset = Title.objects.all()
    serializer_class = TitleReciveSerializer
    # permission_classes = [,]
    # filterset_class = TitleFilter
    filterset_fields = ['name']
    ordering_fields = ('name',)

    def get_serializer_class(self):
        """
        Переопределяем метод get_serializer_class()
        для проверки какаяоперация REST
        была использована и возвращаем серриализаторы
        для записи и чтения.
        """
        if self.action in ['list', 'retrieve']:
            return TitleCreateSerializer
        return TitleReciveSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Отзывов."""

    serializer_class = ReviewsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
    """Вьюсет модели Комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
