# Generated by Django 3.2.5 on 2022-05-26 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_group_groupuser'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='groupuser',
            unique_together={('user', 'group')},
        ),
    ]
