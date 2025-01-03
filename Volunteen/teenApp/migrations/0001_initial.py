# Generated by Django 5.0.1 on 2024-12-15 14:49

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('childApp', '0001_initial'),
        ('mentorApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(help_text='Enter the task details', verbose_name='Task Description')),
                ('deadline', models.DateField(db_index=True, help_text='Specify the deadline for the task', verbose_name='Deadline')),
                ('completed', models.BooleanField(default=False, help_text='Mark as completed', verbose_name='Completed')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('img', models.ImageField(blank=True, default='defaults/no-image.png', null=True, upload_to='media/images/', verbose_name='Image')),
                ('points', models.IntegerField(help_text='Enter the points for the task', verbose_name='Points')),
                ('additional_details', models.TextField(blank=True, help_text='Enter any additional details about the task', null=True, verbose_name='Additional Details')),
                ('new_task', models.BooleanField(default=True, help_text='Indicates if the task is new for the child', verbose_name='New Task')),
                ('viewed', models.BooleanField(default=False, help_text='Indicates if the child has viewed the task', verbose_name='Viewed')),
                ('total_bonus_points', models.IntegerField(default=0, help_text='Total bonus points assigned to this task', verbose_name='Total Bonus Points')),
                ('completed_date', models.DateTimeField(blank=True, help_text='The date when the task was completed', null=True, verbose_name='Completed Date')),
                ('admin_max_points', models.IntegerField(default=0, help_text='Max bonus points assigned to this task', verbose_name='Max Bonus Points')),
                ('duration', models.TextField(help_text='Enter the duration of the task', verbose_name='Duration')),
                ('assigned_children', models.ManyToManyField(blank=True, related_name='assigned_tasks', to='childApp.child', verbose_name='Assigned Children')),
                ('assigned_mentors', models.ManyToManyField(blank=True, related_name='assigned_tasks', to='mentorApp.mentor', verbose_name='Assigned Mentors')),
            ],
        ),
        migrations.CreateModel(
            name='TaskCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completion_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('bonus_points', models.IntegerField(default=0)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='childApp.child')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teenApp.task')),
            ],
            options={
                'unique_together': {('child', 'task')},
            },
        ),
    ]
