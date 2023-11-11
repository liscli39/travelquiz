# Generated by Django 3.2.5 on 2023-11-09 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20231109_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'lựa chọn'), (1, 'tự luận'), (2, 'dự đoán')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'nam'), (0, 'nữ')], null=True),
        ),
    ]
