from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        r'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
