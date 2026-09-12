"""Initial migration for the `thoughts` app.

Review used to live in the `reviews` app and Post in the `posts` app. Both
models keep their ORIGINAL database tables -- `reviews_review` and
`posts_post` -- via Meta.db_table, so on an existing database every row,
primary key, rating, date and thumbnail path is reused exactly as it was.
No table is renamed, dropped, recreated or copied.

Because the tables are unchanged, this migration is "already true" for any
database that was created before the refactor. Such a database adopts it with:

    python manage.py migrate --fake-initial

which notices that both tables already exist and records the migration as
applied without running any SQL. A brand new database just runs it normally
and gets the two tables created.

The old `reviews` and `posts` apps are removed from INSTALLED_APPS in the same
change, so their migration files are never loaded again. That is why this
migration declares no dependency on them -- one would become a dangling
reference the moment those apps go away.
"""

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    # Required for `migrate --fake-initial` to recognise the existing tables.
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='reviews/thumbnails/')),
            ],
            options={
                'db_table': 'reviews_review',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='posts/thumbnails/')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'posts_post',
            },
        ),
    ]
