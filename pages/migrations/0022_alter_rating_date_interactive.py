# Generated by Django 4.2.11 on 2024-05-04 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0021_alter_rating_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='date',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.CreateModel(
            name='Interactive',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('history', models.JSONField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]