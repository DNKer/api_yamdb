from django.contrib.auth.forms import UserCreationForm

from reviews.models import User


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
