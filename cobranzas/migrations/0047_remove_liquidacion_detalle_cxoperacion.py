# Generated by Django 4.0.4 on 2022-12-07 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0046_remove_liquidacion_cabecera_cxtipooperacion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='liquidacion_detalle',
            name='cxoperacion',
        ),
    ]
