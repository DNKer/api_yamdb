from django.contrib import admin

from reviews.models import Comments, Reviews


@admin.register(Reviews)
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


admin.site.register(Comments)
