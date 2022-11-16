# Generated by Django 3.2.5 on 2022-11-15 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('final', '0004_auto_20221114_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('answer_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('choice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='final.choice')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='final.keywordquestion')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='final.team')),
            ],
        ),
    ]