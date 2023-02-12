from django.conf import settings
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

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

    class Meta():
        abstract = True

    def __str__(self):
        """Возвращаем укороченный текст модели."""
        return (
            self.text[:settings.ADMINS_TEXT_LENGHT] + '...'
            if len(self.text) >= settings.ADMINS_TEXT_LENGHT
            else self.text
        )


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_username]
    )
    email = models.EmailField('Электронная почта', unique=True, max_length=254)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        default=USER
    )
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        null=True
    )

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR


class CategoryAndGenreBase(models.Model):

    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Уникальный идентифиактор',
        help_text='Используйте буквы латиницы, цифры и символы "-" и "_"'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Category(CategoryAndGenreBase):

    class Meta(CategoryAndGenreBase.Meta):
        verbose_name = 'Категория произведения'
        verbose_name_plural = 'Категории произведений'


class Genre(CategoryAndGenreBase):

    class Meta(CategoryAndGenreBase.Meta):
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанр произведений'


class Title(models.Model):

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=200,
    )
    year = models.IntegerField(
        help_text='Год выхода',
        validators=[validate_year]
    )
    description = models.TextField(
        help_text='Описание',
        blank=True
    )
    genre = models.ManyToManyField(Genre, help_text='Жанр')
    category = models.ForeignKey(
        Category,
        help_text='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    class Meta:
        ordering = ['name']


class ReviewAndCommentBase(models.Model):

    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        default_related_name = '%(model_name)ss'
        ordering = ('-pub_date',)


class Review(ReviewAndCommentBase):

    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
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

    class Meta(ReviewAndCommentBase.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]


class Comment(ReviewAndCommentBase):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
