# Generated by Django 4.0.4 on 2022-05-17 03:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0008_remove_datos_participantes_cxclase'),
        ('clientes', '0011_remove_datos_generales_ctobjetosocial_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datos_generales',
            name='cxclase',
            field=models.ForeignKey(default='A', on_delete=django.db.models.deletion.CASCADE, to='empresa.clases_cliente', to_field='cxclase'),
        ),
    ]
