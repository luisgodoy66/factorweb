# Generated by Django 4.0.4 on 2023-06-03 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0004_puntos_emision'),
    ]

    operations = [
        migrations.AddField(
            model_name='puntos_emision',
            name='nultimasecuencia',
            field=models.IntegerField(default=0),
        ),
    ]