# Generated by Django 4.0.5 on 2022-07-14 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_trainhistory_options_trainhistory_reps_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainhistory',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='app.trainplan'),
        ),
    ]
