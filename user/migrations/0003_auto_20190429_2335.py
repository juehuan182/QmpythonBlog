# Generated by Django 2.1.3 on 2019-04-29 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190423_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='avatar',
            field=models.URLField(blank=True, default='/media/avatar/qmpython_avatar.png', max_length=100, verbose_name='头像'),
        ),
    ]
