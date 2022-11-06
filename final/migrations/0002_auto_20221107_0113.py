# Generated by Django 3.2.5 on 2022-11-06 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('final', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='point',
            field=models.IntegerField(default=0),
        ),
    ]