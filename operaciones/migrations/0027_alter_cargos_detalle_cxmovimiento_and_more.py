# Generated by Django 4.0.4 on 2024-07-14 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0026_anexos_cxtipocliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargos_detalle',
            name='cxmovimiento',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='movimientos_clientes',
            name='cxmovimiento',
            field=models.BigIntegerField(null=True),
        ),
    ]
