# Generated by Django 3.2.5 on 2023-11-08 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20231016_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='limit_question',
            field=models.IntegerField(default=20),
        ),
        migrations.AddField(
            model_name='week',
            name='limit_time',
            field=models.IntegerField(default=120000),
        ),
    ]
