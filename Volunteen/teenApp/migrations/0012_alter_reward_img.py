# Generated by Django 5.0.1 on 2024-05-14 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teenApp', '0011_alter_reward_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reward',
            name='img',
            field=models.ImageField(blank=True, default='defaults/no-image.png', null=True, upload_to='media/images/', verbose_name='Image'),
        ),
    ]