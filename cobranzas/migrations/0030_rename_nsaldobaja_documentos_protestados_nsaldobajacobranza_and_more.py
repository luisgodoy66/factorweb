# Generated by Django 4.0.4 on 2022-11-24 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0029_alter_documentos_protestados_accesorio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentos_protestados',
            old_name='nsaldobaja',
            new_name='nsaldobajacobranza',
        ),
        migrations.RenameField(
            model_name='documentos_protestados',
            old_name='nvalorbaja',
            new_name='nvalorbajacobranza',
        ),
        migrations.RemoveField(
            model_name='recuperaciones_cabecera',
            name='chequeprotestado',
        ),
        migrations.AddField(
            model_name='recuperaciones_detalle',
            name='chequeprotestado',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.RESTRICT, to='cobranzas.cheques_protestados'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recuperaciones_detalle',
            name='nvalorbajacobranza',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
