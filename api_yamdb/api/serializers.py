from rest_framework import validators, serializers


from api_yamdb.settings import MAX_SCORE_VALUE, MIN_SCORE_VALUE
from reviews.models import Category, Comment, Genre, Review, Title, User


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email',)


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

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = (
            'id', 'name', 'year', 'description'
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

    # def validate(self, data):
    #     if self.context['request'].method != 'POST':
    #         return data
        

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
