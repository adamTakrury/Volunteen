# Generated by Django 5.0.1 on 2024-05-21 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teenApp', '0015_task_assigned_mentors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='task_id',
        ),
    ]
