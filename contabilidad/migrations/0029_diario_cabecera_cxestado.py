# Generated by Django 4.0.4 on 2023-06-25 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0028_rename_cxasiento_comprobante_egreso_asiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='diario_cabecera',
            name='cxestado',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
