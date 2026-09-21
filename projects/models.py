from django.db import models

# Create your models here.
class Project(models.Model):
    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        max_length=500,
        help_text="A brief overview of the project."
    )

    github_url = models.URLField(
        blank=True,
        help_text="Link to the project's GitHub repository."
    )

    planned_additions = models.TextField(
        blank=True,
        help_text="Features or improvements you plan to add."
    )

    thumbnail = models.ImageField(
        upload_to="projects/thumbnails/",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title