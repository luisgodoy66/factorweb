# Generated by Django 4.0.4 on 2023-02-07 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0019_remove_datos_participantes_cxlocalidad_and_more'),
        ('clientes', '0046_remove_datos_compradores_cxactividad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datos_generales',
            name='cxlocalidad',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='empresa.localidades'),
        ),
    ]