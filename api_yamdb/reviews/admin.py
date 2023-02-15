from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title, User


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Настройка модели Reviews в админке."""

    list_display = (
        'id',
        'author',
        'text',
        'score',
        'pub_date',
    )
    list_filter = ('pub_date',)
    search_fields = (
        'author',
        'text',
    )


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(User)
