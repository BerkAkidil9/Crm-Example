# Data migration: set action_url and action_label for notifications that have task_id

from django.db import migrations


def backfill_task_notification_links(apps, schema_editor):
    Notification = apps.get_model('tasks', 'Notification')
    for n in Notification.objects.filter(task_id__isnull=False).exclude(task_id=0):
        if not n.action_url or not n.action_label:
            n.action_url = f'/tasks/{n.task_id}/'
            n.action_label = 'View Task'
            n.save(update_fields=['action_url', 'action_label'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_add_notification_action_link'),
    ]

    operations = [
        migrations.RunPython(backfill_task_notification_links, noop),
    ]
