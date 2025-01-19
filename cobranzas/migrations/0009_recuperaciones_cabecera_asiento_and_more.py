# Generated by Django 4.0.4 on 2023-09-28 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0042_cuentas_cargosfactoring'),
        ('cobranzas', '0008_cheques_protestados_asiento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recuperaciones_cabecera',
            name='asiento',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='asiento_recuperacion', to='contabilidad.diario_cabecera'),
        ),
        migrations.AlterField(
            model_name='cheques_protestados',
            name='lcontabilizada',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='recuperaciones_cabecera',
            name='lcontabilizada',
            field=models.BooleanField(default=False),
        ),
    ]
