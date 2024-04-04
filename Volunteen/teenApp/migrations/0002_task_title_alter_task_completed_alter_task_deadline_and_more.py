# Generated by Django 5.0.1 on 2024-04-02 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teenApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='title',
            field=models.CharField(default='Untitled', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='completed',
            field=models.BooleanField(default=False, help_text='Mark as completed', verbose_name='Completed'),
        ),
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateField(db_index=True, help_text='Specify the deadline for the task', verbose_name='Deadline'),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(help_text='Enter the task details', verbose_name='Task Description'),
        ),
    ]
