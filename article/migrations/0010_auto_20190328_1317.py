# Generated by Django 2.1.3 on 2019-03-28 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0009_auto_20190328_1001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advertising',
            old_name='end_date',
            new_name='end_time',
        ),
    ]
