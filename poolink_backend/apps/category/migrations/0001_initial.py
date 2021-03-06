# Generated by Django 3.1.12 on 2021-07-04 11:24

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import poolink_backend.bases.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='비고')),
                ('is_active', models.BooleanField(blank=True, default=True, null=True, verbose_name='활성화 여부')),
                ('name', models.TextField(help_text='카테고리 이름입니다.', verbose_name='카테고리')),
                ('image', models.ImageField(help_text='카테고리의 이미지입니다.', upload_to='media', verbose_name='카테고리 이미지')),
            ],
            options={
                'verbose_name': '카테고리',
                'verbose_name_plural': '카테고리',
            },
            bases=(poolink_backend.bases.models.UpdateMixin, models.Model),
        ),
    ]
