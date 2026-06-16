from django.contrib import admin

from .models import Genre, Author, Book, BookInstance, Review


admin.site.register(Genre)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'date_of_birth',
        'date_of_death',
    )

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name')
        }),
        ('Dates', {
            'fields': ('date_of_birth', 'date_of_death')
        }),
    )


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'book',
        'borrower',
        'status',
        'due_back',
        'id',
    )

    list_filter = (
        'status',
        'due_back',
    )

admin.site.register(Review)