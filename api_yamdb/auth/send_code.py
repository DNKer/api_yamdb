import secrets

from django.conf import settings
from django.core.mail import send_mail


rnd = secrets.SystemRandom()


def send_mail_with_code(data):
    email = data['email']
    confirmation_code = rnd.randint(
        settings.MIN_CONFIRMATION_CODE_VALUE,
        settings.MAX_CONFIRMATION_CODE_VALUE
    )
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True
    )
    return confirmation_code
