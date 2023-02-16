from django.core.exceptions import ValidationError
from django.utils import timezone


def check_future_year(value):
    """
    Проверка на корректность года
    выхода произведения.
    """

    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'{value} не может быть больше {now}'
        )
