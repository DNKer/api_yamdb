import os
import os.path

from django.core.exceptions import ValidationError
from django.db.models import Avg
from rest_framework import serializers
from reviews.models import (ROLE_CHOICES, Category, Comment, Genre, Review,
                            Title, User)

from api_yamdb.settings import (CONFIRMATION_DIR, MAX_SCORE_VALUE,
                                MIN_SCORE_VALUE)


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор формы регистрации
    """

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('Недопустимый username')
        return username


class ActivationSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения JWT-токена
    """
    confirmation_code = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate_username(self, username):
        if 2 >= len(username) >= 150:
            return ValidationError('')
        return username

    def validate(self, data):
        username = data['username']
        path = f'{CONFIRMATION_DIR}/{username}.env'
        if not os.path.exists(path):
            raise ValidationError(
                {"Ошибка": 'Получите новый код подтверждения'}
            )
        with open(path) as f:
            confirmation_code = int(f.read())
            if confirmation_code != int(data['confirmation_code']):
                raise ValidationError(
                    {"Ошибка": 'Неверный код подтверждения'}
                )
            f.close()
            os.remove(path)
            return data


class AdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор работы администратора с доступом к ролям
    """
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class UsersSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User
    """
    username = serializers.SlugField(max_length=32)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )
        read_only_fields = ('username', 'email', 'role',)


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

    name = serializers.CharField(
        max_length=200,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = (
            '__all__'
        )


class TitleReciveSerializer(serializers.ModelSerializer):
    """Сериализатор получения произведений."""

    category = CategorySerializer(
        read_only=True,
    )
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description',
        )

    def get_rating(self, obj):
        """Рассчитываем рейтинг произведения."""
        return obj.reviews_title.aggregate(Avg('score')).get('score__avg')


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
        """Проверяем, что отзыв на произведение не был написан."""
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=author, title__id=title_id).exists():
            raise serializers.ValidationError('Нельзя дважды писать отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date',
        )
