# Generated by Django 3.1.12 on 2021-07-04 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_category_color'),
        ('users', '0005_auto_20210701_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='prefer',
            field=models.ManyToManyField(blank=True, null=True, related_name='prefer_category', to='category.Category'),
        ),
    ]