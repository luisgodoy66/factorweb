# Generated by Django 4.0.4 on 2023-06-05 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0012_ampliaciones_plazo_cabecera_lfacturagenerada'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='desembolsos',
            name='nporcentajeiva',
        ),
        migrations.AddField(
            model_name='ampliaciones_plazo_cabecera',
            name='nporcentajeiva',
            field=models.DecimalField(decimal_places=2, default=12, max_digits=5),
        ),
        migrations.AddField(
            model_name='asignacion',
            name='nporcentajeiva',
            field=models.DecimalField(decimal_places=2, default=12, max_digits=5),
        ),
    ]
