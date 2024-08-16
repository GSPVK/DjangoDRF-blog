# Generated by Django 5.1 on 2024-08-16 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(1, 'Like'), (0, 'Neutral'), (-1, 'Dislike')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(1, 'Like'), (0, 'Neutral'), (-1, 'Dislike')])),
                ('obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='blog.comment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]