# Generated by Django 3.2.5 on 2022-11-18 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('final', '0007_auto_20221117_2245'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='point',
            new_name='point_first',
        ),
        migrations.AddField(
            model_name='team',
            name='point_second',
            field=models.IntegerField(default=0),
        ),
    ]
