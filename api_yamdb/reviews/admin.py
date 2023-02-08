from django.contrib import admin
<<<<<<< HEAD

from reviews.models import (
    Category, Comment, Genre, Review, Title, User
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('review',)
    list_filter = ('review',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'description',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'role',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'
=======
from reviews.models import Category, Comment, Genre, Review, Title, User
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4


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
<<<<<<< HEAD
=======


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(User)
>>>>>>> 0452ae49e799016e42a273e25f09b8271441e8e4
