from django.db import models

# Create your models here.
class SiteProfile(models.Model):
    name = models.CharField(max_length=100)

    tagline = models.CharField(
        max_length=200,
        blank=True,
    )

    intro = models.CharField(
        max_length=300,
        blank=True
    )

    about_body = models.TextField(
        blank=True
    )

    site_story = models.TextField(
        blank=True
    )

    interests = models.TextField(
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )

    github_url = models.URLField(
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AboutSitePage(models.Model):
    title = models.CharField(
        max_length=100,
        default="About This Site"
    )

    intro = models.TextField()

    what_is_krushcomics = models.TextField()

    deployment_description = models.TextField()

    why_i_built_it = models.TextField()

    planned_improvements = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title