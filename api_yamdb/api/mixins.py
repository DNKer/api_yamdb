<<<<<<< HEAD
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin
)
=======
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
from rest_framework.viewsets import GenericViewSet


class ModelMixinSet(
    CreateModelMixin, ListModelMixin,
    DestroyModelMixin, GenericViewSet
):
    pass
