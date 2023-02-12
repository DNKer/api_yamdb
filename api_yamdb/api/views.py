from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework import filters, status, viewsets
from rest_framework import permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .mixins import GenresCategoriesViewSet
from .permissions import (IsAdmin, IsReadOnly, IsStaff)
from reviews.models import Category, Genre, Review, Title
from .serializers import (
    BasicUserSerializer, CategorySerializer,
    CommentSerializer, FullUserSerializer, GenreSerializer,
    ReadTitlesSerializer, ReviewCreateSerializer, ReviewSerializer,
    SignupUserSerializer, TokenRequestSerializer,
    UpdateTitlesSerializer
)
from .ulitites import generate_confirmation_code


User = get_user_model()


@api_view(['POST'])
def signup(request):
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


@api_view(['POST'])
def token(request):
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


class UserViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review


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


class ReviewViewSet(viewsets.ModelViewSet):
    """Получить все отзывы."""

    serializer_class = ReviewSerializer
    permission_classes = (IsStaff,)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_title(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех произведений."""

    permission_classes = (IsReadOnly | IsAdmin, )
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    ordering_fields = ['name', 'rating']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadTitlesSerializer
        return UpdateTitlesSerializer


class CategoryViewSet(GenresCategoriesViewSet):
    """Получить список всех категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(GenresCategoriesViewSet):
    """Получить список всех жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
