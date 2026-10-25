from django.contrib import admin

from .models import SecurityQuestion


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ("order", "prompt")
    # Answers can only be set with `manage.py set_coco_questions`.
    readonly_fields = ("answer_hashes",)
