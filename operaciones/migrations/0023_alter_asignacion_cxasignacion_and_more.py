# Generated by Django 4.0.4 on 2022-06-18 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0022_alter_asignacion_cxtipofactoring'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='cxasignacion',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='cargos_detalle',
            name='cxasignacion',
            field=models.CharField(blank=True, max_length=8),
        ),
    ]
