from django.core.exceptions import ValidationError
from django.db import models

MAX_HINTS = 3


class SecurityQuestion(models.Model):
    """
    One of the security questions on the unlock screen.

    Jake enters these with `manage.py set_coco_questions`. Answers are
    never stored: only salted hashes of their normalized form.
    """

    order = models.PositiveSmallIntegerField(unique=True)
    prompt = models.TextField()
    answer_hashes = models.JSONField(default=list)
    hints = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Question {self.order}"

    def clean(self):
        if not isinstance(self.hints, list) or len(self.hints) > MAX_HINTS:
            raise ValidationError({"hints": f"Up to {MAX_HINTS} hints."})
