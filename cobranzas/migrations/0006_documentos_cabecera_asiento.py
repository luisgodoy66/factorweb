# Generated by Django 4.0.4 on 2023-07-02 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0032_rename_lordeb_cuentas_nivel1_lorden'),
        ('cobranzas', '0005_cargos_cabecera_lcontabilizada_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos_cabecera',
            name='asiento',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='asiento_cobranza', to='contabilidad.diario_cabecera'),
        ),
    ]