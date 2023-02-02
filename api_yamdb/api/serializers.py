from rest_framework import serializers
from reviews.models import Category, Genre, Title, User


class SighnUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',)


class NotAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User для изменения
    пользователем своего аккаунта.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
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
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleReciveSerializer(serializers.ModelSerializer):
    """Сериализатор получения произведений."""
    category = serializers.SlugRelatedField(read_only=True, slug_field='name')
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('id', 'name',
                            'year', 'description')
