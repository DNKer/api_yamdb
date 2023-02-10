from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from .permissions import IsAdmin, IsReadOnly


class GenresCategoriesViewSet(mixins.CreateModelMixin,
    mixins.DestroyModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = (IsReadOnly | IsAdmin, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('=name',)
    lookup_field = 'slug'
