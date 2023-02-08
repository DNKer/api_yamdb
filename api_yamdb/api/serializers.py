from rest_framework import validators, serializers
from api_yamdb.settings import MAX_SCORE_VALUE, MIN_SCORE_VALUE

from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import  serializers
from reviews.models import (
    Category, Comment, Genre, Review, Title, User,
    USERNAME_LENGTH, EMAIL_LENGTH, CONFIRMATION_CODE_LENGTH
)
from reviews.validators import (UsernameValidation)



class SignUpSerializer(serializers.Serializer, UsernameValidation):
    """Сериализатор регистрации."""
    username = serializers.CharField(max_length=USERNAME_LENGTH,)
    email = serializers.EmailField(max_length=EMAIL_LENGTH,)
    class Meta:
        model = User
        fields = ('email', 'username')

    def create(self, validated_data):
        """https://www.django-rest-framework.org/api-guide/serializers/
        #Savinginstances%23Savinginstances"""
        return User(**validated_data)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_LENGTH,)
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH
    )


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class NotAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User для изменения
    пользователем своего аккаунта.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )
        read_only_fields = ('username', 'email', 'role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        exclude = ('id', )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        exclude = ('id', )
        model = Genre


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    year = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'rating', 'genre', 'category',
        )


class TitleReciveSerializer(serializers.ModelSerializer):
    """Сериализатор получения произведений."""

    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        read_only_fields = ('__all__',)
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date',
        )

    def validate_score(self, value):
        """Проверка выставленной оценки в сериализаторе."""
        if not MIN_SCORE_VALUE <= value <= MAX_SCORE_VALUE:
            raise serializers.ValidationError(
                'Оценка может быть только от 1 до 10!'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        title = get_object_or_404(
            Title,
            id=self.context['view'].kwargs.get('title_id')
        )
        if Review.objects.filter(title=title, author=request.user):
            raise ValidationError('Нельзя оставить больше одного отзыва ')
        return data
        

class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date',
        )
