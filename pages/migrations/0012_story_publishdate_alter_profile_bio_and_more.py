# Generated by Django 4.2.11 on 2024-04-25 07:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0011_remove_profile_id_profile_userid_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='PublishDate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(default='Write here about you ,for other authors!', null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='profiles/default_profile.png', null=True, upload_to='profiles/'),
        ),
        migrations.AlterField(
            model_name='story',
            name='author',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
