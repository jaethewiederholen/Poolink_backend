# Generated by Django 3.1.12 on 2021-08-07 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_auto_20210711_2246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id'], 'verbose_name': '카테고리', 'verbose_name_plural': '카테고리'},
        ),
    ]
