from django.contrib import admin
from .models import Review, Post

# Register your models here.
# Reviews and Posts stay separately manageable, both listed under "Thoughts".
# Site-wide admin branding lives in core/admin.py and is untouched.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'body')
    ordering = ('-created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'body')
    ordering = ('-created_at',)
