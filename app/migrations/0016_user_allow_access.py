# Generated by Django 3.2.5 on 2022-09-08 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_week_show_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allow_access',
            field=models.BooleanField(default=False),
        ),
    ]
