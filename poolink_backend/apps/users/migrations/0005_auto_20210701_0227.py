# Generated by Django 3.1.12 on 2021-06-30 17:27

from django.db import migrations
import poolink_backend.apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210701_0007'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', poolink_backend.apps.users.models.UserManager()),
            ],
        ),
    ]
