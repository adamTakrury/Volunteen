# Generated by Django 5.0.1 on 2024-05-14 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teenApp', '0006_reward_shop_shop_max_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='media/images/', verbose_name='Image'),
        ),
    ]
