# Generated by Django 4.0.4 on 2024-07-28 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0032_rename_ncuotas_pagares_ncantidadcuotas_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagares',
            name='dultimacobranza',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='pagares',
            name='cxestado',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
