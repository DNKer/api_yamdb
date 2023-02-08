import os
import secrets

from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes

from api.mixins import ModelMixinSet
from api.permisions import (IsAdminOrReadOnly, IsAuthorOrReadOnly,
                            IsModeratorOrReadOnly, IsAuthenticatedOrAdmin)
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
    TokenSerializer
)
from api_yamdb.settings import CONFIRMATION_DIR
from core.token import get_tokens_for_user
from reviews.models import Category, Genre, Review, Title, User
from rest_framework_simplejwt.settings import api_settings


RANGE_RANDOMIZE:int = 1000000

@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(
            email=serializer.validated_data.get('email'),
            username=serializer.validated_data.get('username'),
        )
    except IntegrityError:
        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )
    user.confirmation_code = str(secrets.randbelow(RANGE_RANDOMIZE))
    user.save()
    send_mail(
        subject='Код подтверждения сервисе YaMDb',
        message=f'Ваш код подтверждения {user.confirmation_code}',
        from_email='YamDB@mail.ru',
        recipient_list=[user.email, ],
        fail_silently=True
    )
    serializer.save()
    with open(f'{CONFIRMATION_DIR}/{user.username}.env', mode='w') as f:
       f.write(str(user.confirmation_code))    
    return Response(serializer.data, status=status.HTTP_200_OK)

#class SignUp(APIView):

#    permission_classes = (permissions.AllowAny,)

#    def post(request):
#       serializer = SignUpSerializer(data=request.data)
#        confirmation_code = secrets.randbelow(1000000)
#        if serializer.is_valid():
#            email = request.data['email']
#            username = request.data['username']
#            send_mail(
#                'Код подтверждения',
#               f'Ваш код подтверждения {confirmation_code}',
#                'YamDB@mail.ru',
#                [email],
#                fail_silently=True
#            )
#            serializer.save()
#            with open(f'{CONFIRMATION_DIR}/{username}.env', mode='w') as f:
#                f.write(str(confirmation_code))
#            return JsonResponse(
#                {"message": "Код подтверждения отправлен на почту"}
#            )
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    """https://jpadilla.github.io/django-rest-framework-jwt/"""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    user_code = int(request.data['confirmation_code'])
    if (user_code == serializer.validated_data.get(
            'confirmation_code')) and user_code:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODEHANDLER
            payload = jwt_payload_handler(request.user)
            token = jwt_encode_handler(payload)
            return Response({'token': token}, status=status.HTTP_200_OK)
    user_code = ''
    user.save()
    return Response('неверный код подтверждения', status=status.HTTP_400_BAD_REQUEST)

"""
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
                token_access = token["access"]
                f.close()
                os.remove(path)
                return Response({'token': str(token_access)},
                                status=status.HTTP_201_CREATED)
            raise ValidationError('Неверный код')"""


class UsersViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели User.
    Администратор имеет полные права доступа.
    Пользователь может просматривать и редактировать свой аккаунт.
    """
    
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'


    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='me')
    def me_accaunt_view(self, request):
        """Просмотр и изменение своего аккаунта."""
        if request.method != 'PATCH':
            return Response(self.get_serializer(request.user).data)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)

"""    @api_view(['GET', 'PATCH'])
    def get_current_user_info(self, request):
        """"""Просмотр и изменение своего аккаунта."""""""
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
        return Response(serializer.data)"""


class CategoryViewSet(ModelMixinSet):
    """
    Получить список всех категорий.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """
    Получить список всех жанров.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех произведений.
    """
    queryset = Title.objects.all()
    search_fields = ('genre__slug',)
    filterset_fields = ('genre__slug',)
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitleReciveSerializer


    def get_serializer_class(self):
        """
        Переопределяем метод get_serializer_class()
        для проверки какаяоперация REST
        была использована и возвращаем серриализаторы
        для записи и чтения.
        """

        def get_serializer_class(self):
            if self.request.method in SAFE_METHODS:
                return TitleReciveSerializer
        return TitleCreateSerializer        
        """if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReciveSerializer
        if self.action in ['list', 'retrieve']:
            return TitleCreateSerializer
        return TitleReciveSerializer"""


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Отзывов."""

    serializer_class = ReviewsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    

    """permission_classes = (
        (IsAuthorOrReadOnly, IsModeratorOrReadOnly, IsAdminOrReadOnly),
    )"""

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,
                          IsModeratorOrReadOnly)

    def get_queryset(self):
        current_review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id')
        )
        return current_review.comments.all()

    def perform_create(self, serializer):
        title = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title)
        serializer.save(author=self.request.user, review=review)

