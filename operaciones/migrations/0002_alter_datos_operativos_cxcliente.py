# Generated by Django 4.0.4 on 2023-04-18 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_alter_datos_compradores_cxclase'),
        ('operaciones', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_operativos',
            name='cxcliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datos_operativos', to='clientes.datos_generales'),
        ),
    ]
