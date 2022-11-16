# Generated by Django 3.2.5 on 2022-11-14 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('final', '0003_auto_20221114_1028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='username',
            new_name='socket_id',
        ),
        migrations.RemoveField(
            model_name='team',
            name='name',
        ),
        migrations.AddField(
            model_name='team',
            name='team_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]