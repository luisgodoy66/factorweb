# Generated by Django 4.0.4 on 2023-01-16 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0050_cargos_cabecera_cargos_detalle'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargos_cabecera',
            name='nsobrepago',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]