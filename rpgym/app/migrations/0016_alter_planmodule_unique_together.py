# Generated by Django 4.1 on 2022-09-04 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0015_planmodule_done"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="planmodule",
            unique_together={("plan", "module")},
        ),
    ]