# Generated by Django 4.0.4 on 2022-10-06 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0039_remove_datos_compradores_ctemailfacturacionelectronica_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cuentas_bancarias',
            old_name='cxcliente',
            new_name='cxparticipante',
        ),
    ]
