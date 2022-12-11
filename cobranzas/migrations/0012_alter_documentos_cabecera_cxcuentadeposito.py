# Generated by Django 4.0.4 on 2022-10-17 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0017_alter_cuentas_bancarias_ctrutaarchivobanco_and_more'),
        ('cobranzas', '0011_alter_documentos_cabecera_cxcuentatransferencia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentos_cabecera',
            name='cxcuentadeposito',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='banco_deposito', to='empresa.cuentas_bancarias'),
        ),
    ]
