# Generated by Django 4.0.4 on 2023-07-26 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0015_rename_lcargo_movimientos_maestro_litemfactura'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='lfacturagenerada',
            field=models.BooleanField(default=False),
        ),
    ]
