# Generated by Django 4.0.6 on 2022-07-15 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_trainhistory_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainhistory',
            name='plan_module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history', to='app.planmodule'),
        ),
    ]
