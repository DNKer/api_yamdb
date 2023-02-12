from django.views.generic import CreateView

from reviews.forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm