from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import TitleFilter
from .mixins import ModelMixinSet
from reviews.models import Category, Genre, Title, User
from .serializers import (
    CategorySerializer, GenreSerializer, NotAdminSerializer,
    TitleCreateSerializer, TitleReciveSerializer, UsersSerializer
)


class UsersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели User.
    Администратор имеет полные права доступа.
    Пользователь может просматривать и редактировать свой аккаунт.
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminUser,]
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
    #permission_classes = (,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """
    Получить список всех жанров.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    #permission_classes = (,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """
    Получить список всех произведений.
    """
    queryset = Title.objects.all()
    serializer_class = TitleReciveSerializer
    #permission_classes = [,]
    filterset_class = TitleFilter
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
