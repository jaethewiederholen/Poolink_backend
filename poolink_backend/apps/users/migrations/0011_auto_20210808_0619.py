# Generated by Django 3.1.12 on 2021-08-07 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20210807_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='유니크한 유저 이름입니다.', max_length=70, verbose_name='유저 이름'),
        ),
    ]
