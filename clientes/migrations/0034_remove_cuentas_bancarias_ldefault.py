# Generated by Django 4.0.4 on 2022-08-23 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0033_alter_cuentas_bancarias_cxcliente_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cuentas_bancarias',
            name='ldefault',
        ),
    ]
