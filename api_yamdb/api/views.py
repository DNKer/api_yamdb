# TODO: Боб - Разобраться с тем что возвращают методы
# Дописать Permissions
# Здесь или в Сериализаторах разобраться с обязательными полями
# Насовать Exeptions в SighnUp & Activation

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse
from core.token import get_tokens_for_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import secrets
from django.core.mail import send_mail
from reviews.models import User
from api_yamdb.settings import CONFIRMATION_DIR
from django.core.exceptions import ValidationError
import os
# from .filters import TitleFilter
from .mixins import ModelMixinSet
from reviews.models import Category, Genre, Title, User
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          NotAdminSerializer,
                          TitleCreateSerializer,
                          TitleReciveSerializer,
                          UsersSerializer,
                          SighnUpSerializer,
                          )


class SighnUp(APIView):
    permission_classes = [AllowAny,]

    def post(self, request,):
        serializer = SighnUpSerializer(data=request.data)
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

            return JsonResponse({"message": "Код подтверждения отправлен на почту"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Activation(APIView):
    permission_classes = [AllowAny,]

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
    permission_classes = [AllowAny,]  # IsAdminUser
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


class TitleViewSet(ModelViewSet):
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


class CommentViewSet(viewsets.ModelViewSet):
    """
    Получить список всех комментариев.
    """
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Получить список всех отзывов.
    """
    pass
