# Generated by Django 3.2.5 on 2023-10-11 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_answer_answer_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='raw_password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
