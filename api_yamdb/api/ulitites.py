import random
import string

# Storing the value digits and letters in variable result
CONFIRMATION_CODE_CHARACTERS = string.digits + string.ascii_letters


def generate_confirmation_code(length):
    """Функция генерации кода доступа."""
    return ''.join(
        random.choice(CONFIRMATION_CODE_CHARACTERS) for _ in range(length))
