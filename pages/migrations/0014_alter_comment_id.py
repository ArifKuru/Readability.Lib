# Generated by Django 4.2.11 on 2024-04-25 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0013_alter_story_publishdate_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]