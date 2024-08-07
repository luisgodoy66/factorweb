# Generated by Django 4.0.4 on 2024-07-27 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bases', '0011_alter_empresas_ctnombre'),
        ('operaciones', '0031_pagares_pagare_detalle'),
        ('contabilidad', '0044_alter_cuentas_cargosfactoring_cargo_and_more'),
        ('empresa', '0017_alter_otros_cargos_movimiento'),
        ('cobranzas', '0011_pagare_cabecera_pagare_detalle'),
        ('clientes', '0007_alter_personas_juridicas_cxtipoempresa'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pagare_detalle',
            name='cuota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.pagare_detalle'),
        ),
        migrations.AddField(
            model_name='pagare_detalle',
            name='cxusuariocrea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagare_detalle',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='asiento',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='asiento_cobranza_pagare', to='contabilidad.diario_cabecera'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxaccesorio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.chequesaccesorios'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxcheque',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cheque_cobranza_pagare', to='cobranzas.cheques'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxcliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_cobranza_pagare', to='clientes.datos_generales'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxcuentadeposito',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='banco_deposito_pagare', to='empresa.cuentas_bancarias'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxcuentatransferencia',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='clientes.cuentas_bancarias'),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='cxusuariocrea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagare_cabecera',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
        ),
    ]
