from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import MAX_SCORE_VALUE, MIN_SCORE_VALUE
from core.models import CreatedModel


class Reviews(CreatedModel):
    """Модель отзывов."""

    author = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='reviews_author',
        verbose_name='Автор отзыва',
    )
    title = models.ForeignKey(
        'Titles',
        on_delete=models.CASCADE,
        related_name='reviews_title',
        verbose_name='Отзыв к произведению'

    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        help_text='Поставьте оценку от 1 до 10',
        validators=(
            MinValueValidator(
                MIN_SCORE_VALUE,
                'Оценка должна быть не меньше 1!'
            ),
            MaxValueValidator(
                MAX_SCORE_VALUE,
                'Оценка должна быть не больше 10!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comments(CreatedModel):
    """Модель комментариев к отзыву."""

    author = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='comments_author',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='comments_review',
        verbose_name='Комментарии к отзыву',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
