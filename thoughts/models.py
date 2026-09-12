from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
#
# Review and Post moved here from the old `reviews` and `posts` apps.
# Each model keeps its original database table via Meta.db_table so the
# existing rows are reused as-is -- no table was renamed, dropped or
# recreated. See thoughts/migrations/0001_initial.py.


class Review(models.Model):
    # Lets the combined Thoughts feed tell a Review apart from a Post.
    # Plain class attribute, not a database field.
    kind = "review"

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

    class Meta:
        db_table = "reviews_review"

    def __str__(self):
        return f"{self.title} | {self.rating}/10"


class Post(models.Model):
    # Lets the combined Thoughts feed tell a Post apart from a Review.
    # Plain class attribute, not a database field.
    kind = "post"

    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(
        upload_to="posts/thumbnails/",
        blank=True,
        null=True
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posts_post"

    def __str__(self):
        return self.title
