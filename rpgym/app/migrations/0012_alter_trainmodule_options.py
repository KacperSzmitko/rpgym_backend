# Generated by Django 4.0.6 on 2022-07-22 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_trainmodule_options_trainmodule_creation_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainmodule',
            options={'ordering': ['-creation_date', 'pk']},
        ),
    ]
