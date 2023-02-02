from django.db import models

from api_yamdb.settings import ADMINS_TEXT_LENGHT


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
            self.text[:ADMINS_TEXT_LENGHT] + '...'
            if len(self.text) >= ADMINS_TEXT_LENGHT
            else self.text
        )
