import datetime as dt
import re

from django.core.exceptions import ValidationError

USERNAME_REGEX = re.compile(r'^[\w.@+-]+$')


def validate_username(value):
    """Проверка имени пользователя на допустимые символы."""
    if not USERNAME_REGEX.match(value):
        raise ValidationError(
            message='допустимы только буквы, цифры и @/./+/-/_',
            code='invalid'
        )
    if value == 'me':
        raise ValidationError(
            'Имя пользователя me не может быть использовано',
            code='invalid'
        )

    def __call__(self, value):
        try:
            super().__call__(value)
            if value == 'me':
                raise ValidationError(
                    'Имя пользователя me не может быть использовано',
                    code='invalid'
                )
        return value
