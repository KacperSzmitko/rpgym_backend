# Generated by Django 4.1 on 2022-09-14 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_alter_planmodule_order_in_plan"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainplan",
            name="started",
            field=models.BooleanField(default=False),
        ),
    ]
