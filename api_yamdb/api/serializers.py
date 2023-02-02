from rest_framework import validators, serializers

from api_yamdb.settings import MAX_SCORE_VALUE, MIN_SCORE_VALUE
from reviews.models import Comments, Reviews


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = Reviews
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Reviews.objects.all(),
                fields=('author', 'title',),
                message='Нельзя дважды писать отзыв на одно произведение!'
            ),
        )

    def validate_score(self, value):
        """Проверка выставленной оценки в сериализаторе."""
        if value not in (
            MIN_SCORE_VALUE <= value <= MAX_SCORE_VALUE
        ):
            raise serializers.ValidationError(
                'Оценка может быть только от 1 до 10!'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date',)
