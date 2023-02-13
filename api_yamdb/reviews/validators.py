import datetime as dt

from django.core.exceptions import ValidationError


def check_future_year(value):
    """
    Проверка на корректность года
    выхода произведения.
    """
    if value > dt.date.today().year:
        raise ValidationError(
            f'Год выхода произведения: {value}, не может быть больше текущего!'
        )
