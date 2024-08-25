# Generated by Django 5.0.6 on 2024-07-18 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0004_rename_game_gameimage_game_alter_gameimage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.URLField(verbose_name='YouTube URL')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='viewer.game')),
            ],
        ),
    ]