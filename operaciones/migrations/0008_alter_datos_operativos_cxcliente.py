# Generated by Django 4.0.4 on 2022-06-07 04:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0024_alter_linea_factoring_hist_cxcliente'),
        ('operaciones', '0007_alter_datos_operativos_cxcliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_operativos',
            name='cxcliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datos_operativos', to='clientes.datos_generales', to_field='cxcliente'),
        ),
    ]
