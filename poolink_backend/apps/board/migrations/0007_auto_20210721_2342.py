# Generated by Django 3.1.12 on 2021-07-21 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0006_auto_20210706_0013'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='board',
            options={'ordering': ['-id'], 'verbose_name': '보드', 'verbose_name_plural': '보드'},
        ),
    ]