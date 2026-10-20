from django.contrib import admin
from .models import CTF, WriteUp

# Register your models here.


@admin.register(CTF)
class CTFAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "year",
        "slug",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name", "year"),
    }


@admin.register(WriteUp)
class WriteUpAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "ctf",
        "category",
        "difficulty",
        "is_published",
        "published_at",
    )

    list_filter = (
        "is_published",
        "ctf",
        "category",
        "difficulty",
    )

    search_fields = (
        "title",
        "summary",
        "body",
        "tools",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (None, {
            "fields": (
                "ctf",
                "title",
                "slug",
                "category",
                "difficulty",
                "tools",
                "thumbnail",
            ),
        }),
        ("Write-Up", {
            "fields": (
                "summary",
                "body",
                "lessons_learned",
            ),
        }),
        ("Publishing", {
            "fields": (
                "is_published",
                "published_at",
                "created_at",
                "updated_at",
            ),
        }),
    )
