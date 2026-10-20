from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.
#
# Only CTF write-ups exist for now. Labs and Research will get their own
# models later; to show up in the Security carousel they need a `kind`
# class attribute, a `published_at` date and a `get_absolute_url()`,
# just like WriteUp. See security/services.py.


class CTF(models.Model):
    """One CTF event, e.g. DEADFACE 2026. Groups that event's write-ups."""

    name = models.CharField(
        max_length=200,
        help_text="Event name, e.g. DEADFACE."
    )

    year = models.PositiveSmallIntegerField()

    slug = models.SlugField(
        max_length=80,
        unique=True,
        help_text=(
            "Used in the URL, e.g. deadface-2026. "
            "Include the year so recurring events don't clash."
        )
    )

    website = models.URLField(
        blank=True,
        help_text="Link to the event's site or CTFtime page."
    )

    description = models.TextField(
        blank=True,
        help_text="Optional short description of the event."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-year", "name"]
        verbose_name = "CTF"
        verbose_name_plural = "CTFs"

    def __str__(self):
        return f"{self.name} {self.year}"

    def get_absolute_url(self):
        return reverse("ctf_detail", args=[self.slug])


class WriteUpQuerySet(models.QuerySet):

    def published(self):
        return self.filter(is_published=True)


class WriteUp(models.Model):
    # Lets the combined Security feed tell a write-up apart from future
    # Labs and Research entries. Plain class attribute, not a database field.
    kind = "writeup"

    class Category(models.TextChoices):
        WEB = "web", "Web"
        CRYPTO = "crypto", "Crypto"
        FORENSICS = "forensics", "Forensics"
        NETWORKING = "networking", "Networking"
        REVERSE_ENGINEERING = "reverse-engineering", "Reverse Engineering"
        BINARY_EXPLOITATION = "binary-exploitation", "Binary Exploitation"
        OSINT = "osint", "OSINT"
        STEGANOGRAPHY = "steganography", "Steganography"
        MISC = "misc", "Misc"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"
        INSANE = "insane", "Insane"

    ctf = models.ForeignKey(
        CTF,
        on_delete=models.PROTECT,
        related_name="writeups",
        verbose_name="CTF"
    )

    title = models.CharField(
        max_length=200,
        help_text="Challenge name, e.g. A Pirates Life for Me: Part 1."
    )

    slug = models.SlugField(
        max_length=80,
        help_text=(
            "Used in the URL. Fills in from the title; "
            "shorten it if you like. Must be unique within the CTF."
        )
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices
    )

    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices
    )

    tools = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated, e.g. Wireshark, Python."
    )

    summary = models.TextField(
        max_length=500,
        help_text="Short description of what the challenge involved."
    )

    body = models.TextField(
        verbose_name="write-up",
        help_text="Full technical walkthrough. Markdown is supported."
    )

    lessons_learned = models.TextField(
        blank=True,
        help_text="What you learned from solving it. Markdown is supported."
    )

    thumbnail = models.ImageField(
        upload_to="security/writeups/thumbnails/",
        blank=True
    )

    is_published = models.BooleanField(
        "published",
        default=False,
        help_text=(
            "Leave unchecked until the CTF has ended -- most events "
            "forbid sharing solutions while they are running."
        )
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Filled in automatically the first time you publish."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = WriteUpQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-pk"]
        verbose_name = "write-up"
        constraints = [
            models.UniqueConstraint(
                fields=["ctf", "slug"],
                name="unique_writeup_slug_per_ctf",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.ctf})"

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "writeup_detail",
            args=[self.ctf.slug, self.slug]
        )

    @property
    def tool_list(self):
        """The comma-separated tools field as a clean list."""

        return [
            tool.strip()
            for tool in self.tools.split(",")
            if tool.strip()
        ]
