# Generated by Django 3.2.5 on 2022-06-14 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_groupanswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='submits',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
