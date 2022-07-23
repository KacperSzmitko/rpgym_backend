# Generated by Django 4.0.5 on 2022-07-14 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainhistory',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='trainhistory',
            name='reps',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.DeleteModel(
            name='HistoryUnit',
        ),
    ]
