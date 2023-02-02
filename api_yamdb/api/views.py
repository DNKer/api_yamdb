from rest_framework import permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import (
    CommentSerializer, ReviewsSerializer
)
from reviews.models import Reviews


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Отзывов."""

    serializer_class = ReviewsSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_title(self):
        """Получаем произведение для отзыва."""
        return get_object_or_404(Titles, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получаем queryset."""
        return self.get_title().reviews_title

    def perform_create(self, serializer):
        """Переопределяем метод create."""
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Комментариев."""

    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_review(self):
        """Получаем отзыв для комментария."""
        return get_object_or_404(
            Reviews,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Получаем queryset."""
        return self.get_review().comments_review

    def perform_create(self, serializer):
        """Переопределяем метод create."""
        serializer.save(review=self.get_review(), author=self.request.user)
