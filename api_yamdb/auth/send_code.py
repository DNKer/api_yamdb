import secrets

from django.core.mail import send_mail

from api_yamdb.settings import CONFIRMATION_DIR

rnd = secrets.SystemRandom()


def send_mail_with_code(data):
    email = data['email']
    username = data['username']
    confirmation_code = rnd.randint(100000, 999999)
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения {confirmation_code}',
        'YamDB@mail.ru',
        [email],
        fail_silently=True
    )
    with open(f'{CONFIRMATION_DIR}/{username}.env', mode='w') as f:
        f.write(str(confirmation_code))
