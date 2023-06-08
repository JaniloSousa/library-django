from django.contrib import admin

from library.models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    ...


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...
