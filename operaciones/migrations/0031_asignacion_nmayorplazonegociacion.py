# Generated by Django 4.0.4 on 2022-09-12 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0030_asignacion_dliquidacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignacion',
            name='nmayorplazonegociacion',
            field=models.SmallIntegerField(default=0),
        ),
    ]
