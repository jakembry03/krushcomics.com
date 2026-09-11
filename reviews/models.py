from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Review(models.Model):
    title = models.CharField(max_length=200)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ]
    )
    thumbnail = models.ImageField(
        upload_to="reviews/thumbnails/",
        blank=True,
        null=True
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} | {self.rating}/10"