# Generated by Django 4.0.4 on 2023-05-22 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0003_remove_cuentas_especiales_cxcuentagananciaejercicio_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cuentas_especiales',
            old_name='cxcuentaconjunta',
            new_name='cuentaconjunta',
        ),
    ]
