import os
import os.path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.http import Http404
from rest_framework import serializers

from reviews.models import (
    ROLE_CHOICES, Category, Comment, Genre, Review, Title, User
)

User = get_user_model()


class UsernameSerializer(serializers.Serializer):
    """Сериализатор пользователя."""

    confirmation_code = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            return username
        raise Http404

    def validate(self, data):
        username = data['username']
        path = f'{settings.CONFIRMATION_DIR}/{username}.env'
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
    Сериализатор работы администратора с доступом к ролям.
    """

    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class SignupUserSerializer(UsernameSerializer):
    """Сериализатор авторизации."""

    email = serializers.EmailField(max_length=254)


class TokenRequestSerializer(UsernameSerializer):
    """Сериализатор для token."""

    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH
    )


class FullUserSerializer(serializers.ModelSerializer):
    """Сериализатор для выполнения операций
    пользователями с ролью администратор."""

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        ]


class BasicUserSerializer(FullUserSerializer):
    """Сериализатор для выполнения операций
    пользователями с ролью не администратора."""

    class Meta(FullUserSerializer.Meta):
        read_only_fields = ['role']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


    def validate_score(self, value):
        """Проверка выставленной оценки в сериализаторе."""
        if not (
            settings.MIN_SCORE_VALUE <= value <= settings.MAX_SCORE_VALUE
        ):
            raise serializers.ValidationError(
                'Оценка может быть только от 1 до 10!'
            )
        return value

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title_id)
        if title.reviews.filter(author=author).exists():
            raise serializers.ValidationError(
                'Нельзя писать второй отзыв!'
            )
        return data


class ReadTitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для списка произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'rating', 'genre',
                  'category', 'description')
        read_only_fields = ['__all__']


class UpdateTitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('__all__')
