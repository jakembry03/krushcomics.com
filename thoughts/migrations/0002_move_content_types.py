"""Re-label the existing ContentType rows for Review and Post.

`django_content_type` still holds rows saying Review belongs to `reviews` and
Post belongs to `posts`. Those rows are pointed at by:

  * `auth_permission`  -- add/change/delete/view permissions
  * `django_admin_log` -- the admin history for every edit made so far

Updating the rows in place (rather than letting Django create fresh ones for
`thoughts` and leaving the old pair stale) keeps that history and those
permission assignments attached to the models. Permission codenames such as
`add_review` are unchanged, so nothing is duplicated afterwards.

Nothing here touches the Review or Post tables themselves.
"""

from django.db import migrations

MOVES = [
    # (old app_label, new app_label, model)
    ('reviews', 'thoughts', 'review'),
    ('posts', 'thoughts', 'post'),
]


def _relabel(apps, moves):
    ContentType = apps.get_model('contenttypes', 'ContentType')

    for old_label, new_label, model in moves:
        # If the destination row somehow already exists, leave both alone
        # rather than tripping the (app_label, model) unique constraint.
        if ContentType.objects.filter(app_label=new_label, model=model).exists():
            continue

        ContentType.objects.filter(
            app_label=old_label,
            model=model,
        ).update(app_label=new_label)


def move_content_types(apps, schema_editor):
    _relabel(apps, MOVES)


def unmove_content_types(apps, schema_editor):
    _relabel(apps, [(new, old, model) for old, new, model in MOVES])


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('thoughts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(move_content_types, unmove_content_types),
    ]
