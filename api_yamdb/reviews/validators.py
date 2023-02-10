import re

from django.core.validators import ValidationError

INVALID_USERNAME = 'Недопустимое имя пользователя: "{value}".'
USERNAME_SYMBOLS = re.compile(r'[\w.@+-@./+-]+')
INVALID_USERNAME_SYMBOLS = 'Недопустимые символы: {value}'


class UsernameValidation:
    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(INVALID_USERNAME.format(value=value))
        if not re.match(USERNAME_SYMBOLS, value):
            raise ValidationError(
                INVALID_USERNAME_SYMBOLS.format(
                    value=[
                        symbol for symbol in value if symbol not in ''.join(
                            re.findall(USERNAME_SYMBOLS, value)
                        )
                    ]
                )
        except ValidationError as e:
            if self.exception:
                raise self.exception(e.message, code=e.code)
            raise

def validate_year(value):
    if value > dt.date.today().year:
        raise ValidationError(
            f'Год выхода произведения: {value}, не может быть больше текущего!'
        )
