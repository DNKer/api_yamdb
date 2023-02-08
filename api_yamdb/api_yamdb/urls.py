from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/', include('api.urls')),
    path(
        r'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
