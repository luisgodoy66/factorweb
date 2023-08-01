# Generated by Django 4.0.4 on 2023-07-31 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0017_alter_cargos_detalle_cxmovimiento_and_more'),
        ('contabilidad', '0036_factura_venta_cxtipofactoring_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura_venta',
            name='notadebito',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='factura_notadedebito', to='operaciones.notas_debito_cabecera'),
        ),
    ]
