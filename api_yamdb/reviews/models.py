from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import ADMIN, MODERATOR, USER
from .validators import check_future_year

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляем текст и дату создания."""

    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите ваш текст!',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date')

    def __str__(self):
        """Возвращаем укороченный текст модели."""
        return (
            self.text[:settings.ADMINS_TEXT_LENGHT] + '...'
            if len(self.text) >= settings.ADMINS_TEXT_LENGHT
            else self.text
        )


class User(AbstractUser):
    """Модель Юзера."""

    username = models.SlugField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Пользователь',
        help_text='Введите имя пользователя'
    )

    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        help_text='Выберете роль пользователя'
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        help_text='Фамилия пользователя'
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='XXXX'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель Категорий."""

    name = models.CharField(
        verbose_name='Название категории',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель Жанров."""

    name = models.CharField(
        verbose_name='Название жанра',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=200,
        db_index=True
    )
    year = models.IntegerField(
        verbose_name='Год создания',
        null=True,
        help_text='Год выхода',
        validators=[check_future_year]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=255,
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(CreatedModel):
    """Модель отзывов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_author',
        verbose_name='Автор отзыва',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews_title',
        verbose_name='Отзыв к произведению',
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        help_text='Поставьте оценку от 1 до 10',
        validators=(
            MinValueValidator(
                settings.MIN_SCORE_VALUE,
                'Оценка должна быть не меньше 1!'
            ),
            MaxValueValidator(
                settings.MAX_SCORE_VALUE,
                'Оценка должна быть не больше 10!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'author',
                    'title',
                ],
                name='unique_author_title',
            )
        ]


class Comment(CreatedModel):
    """Модель комментариев к отзыву."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_author',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments_review',
        verbose_name='Комментарии к отзыву',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
