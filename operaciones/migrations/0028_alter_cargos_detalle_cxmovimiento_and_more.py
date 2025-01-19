# Generated by Django 4.0.4 on 2024-07-15 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0016_remove_tasas_factoring_cttasa_movimientos_maestro_and_more'),
        ('operaciones', '0027_alter_cargos_detalle_cxmovimiento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargos_detalle',
            name='cxmovimiento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cargo_movimiento', to='empresa.movimientos_maestro'),
        ),
        migrations.AlterField(
            model_name='movimientos_clientes',
            name='cxmovimiento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='maestro_movimientos', to='empresa.movimientos_maestro'),
        ),
        migrations.DeleteModel(
            name='Movimientos_maestro',
        ),
    ]
