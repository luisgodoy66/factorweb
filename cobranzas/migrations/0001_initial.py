# Generated by Django 4.0.4 on 2023-04-15 18:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bases', '0001_initial'),
        ('cuentasconjuntas', '__first__'),
        ('clientes', '0001_initial'),
        ('operaciones', '__first__'),
        ('empresa', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargos_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcobranza', models.DateTimeField(auto_created=True)),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxcobranza', models.CharField(max_length=8)),
                ('cxformapago', models.CharField(choices=[('EFE', 'Efectivo'), ('CHE', 'Cheque'), ('MOV', 'Movimiento contable'), ('TRA', 'Transferencia'), ('DEP', 'Deposito de accesorio')], max_length=3)),
                ('cxlocalidad', models.CharField(blank=True, max_length=4)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsobrepago', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cxestado', models.CharField(default=' ', max_length=1)),
                ('ddeposito', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cheques',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtipoparticipante', models.CharField(choices=[('D', 'Deudor'), ('C', 'Cliente')], max_length=1)),
                ('ctcheque', models.CharField(max_length=8)),
                ('ctplaza', models.CharField(max_length=30, null=True)),
                ('ctgirador', models.CharField(blank=True, max_length=60)),
                ('cxestado', models.CharField(default=' ', max_length=1)),
                ('nvalor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cxcuentabancaria', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='clientes.cuentas_bancarias')),
                ('cxparticipante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_cheque', to='empresa.datos_participantes')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cheques_protestados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxformacobro', models.CharField(choices=[('CHE', 'Cheque'), ('DEP', 'Deposito de accesorio')], max_length=3)),
                ('dprotesto', models.DateField()),
                ('nvalor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nvalorcartera', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsaldocartera', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('dultimacobranza', models.DateTimeField(null=True)),
                ('cxtipooperacion', models.CharField(max_length=1)),
                ('cheque', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cheque_protestado', to='cobranzas.cheques')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('motivoprotesto', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='operaciones.motivos_protesto_maestro')),
                ('notadedebito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operaciones.notas_debito_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documentos_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcobranza', models.DateField(auto_created=True)),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxcobranza', models.CharField(max_length=8)),
                ('cxformapago', models.CharField(choices=[('EFE', 'Efectivo'), ('CHE', 'Cheque'), ('MOV', 'Movimiento contable'), ('TRA', 'Transferencia'), ('DEP', 'Deposito de accesorio')], max_length=3)),
                ('cxlocalidad', models.CharField(blank=True, max_length=4)),
                ('dliquidacion', models.DateTimeField(null=True)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsobrepago', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('ddeposito', models.DateTimeField(null=True)),
                ('lpagadoporelcliente', models.BooleanField(default=False)),
                ('ldepositoencuentaconjunta', models.BooleanField(default=False)),
                ('cxaccesorio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.chequesaccesorios')),
                ('cxcheque', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cheque_cobranza', to='cobranzas.cheques')),
                ('cxcliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_cobranza', to='clientes.datos_generales')),
                ('cxcuentaconjunta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cuenta_deposito', to='cuentasconjuntas.cuentas_bancarias')),
                ('cxcuentadeposito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='banco_deposito', to='empresa.cuentas_bancarias')),
                ('cxcuentatransferencia', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='clientes.cuentas_bancarias')),
                ('cxtipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tipofactoring_cobranza', to='empresa.tipos_factoring')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documentos_protestados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nvalor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nsaldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nvalorbajacobranza', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsaldobajacobranza', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('dultimacobranza', models.DateTimeField(null=True)),
                ('accesorio', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='operaciones.chequesaccesorios')),
                ('chequeprotestado', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cobranzas.cheques_protestados')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.documentos')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Liquidacion_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxliquidacion', models.CharField(max_length=8)),
                ('cxtipooperacion', models.CharField(choices=[('R', 'Recuperación'), ('C', 'Cobranzas')], max_length=1)),
                ('jcobranzas', models.JSONField()),
                ('nvuelto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsobrepago', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ngao', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ngaoa', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ndescuentodecartera', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nretenciones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nbajas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notros', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('niva', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nneto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ctinstrucciondepago', models.TextField()),
                ('dliquidacion', models.DateTimeField()),
                ('ddesembolso', models.DateTimeField()),
                ('ldesembolsada', models.BooleanField(default=False)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('cxcliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_liquidacion', to='clientes.datos_generales')),
                ('cxtipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tipofactoring_liquidacioncobranzas', to='empresa.tipos_factoring')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recuperaciones_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcobranza', models.DateField(auto_created=True)),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxrecuperacion', models.CharField(max_length=8)),
                ('cxformacobro', models.CharField(choices=[('EFE', 'Efectivo'), ('CHE', 'Cheque'), ('MOV', 'Movimiento contable'), ('TRA', 'Transferencia')], max_length=3)),
                ('cxlocalidad', models.CharField(blank=True, max_length=4)),
                ('dliquidacion', models.DateTimeField(null=True)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsobrepago', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('ddeposito', models.DateTimeField(null=True)),
                ('lpagadoporelcliente', models.BooleanField(default=False)),
                ('ldepositoencuentaconjunta', models.BooleanField(default=False)),
                ('cxcheque', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cheque_recuperacion', to='cobranzas.cheques')),
                ('cxcliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.datos_generales')),
                ('cxcuentaconjunta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cuentaconjunta_deposito', to='cuentasconjuntas.cuentas_bancarias')),
                ('cxcuentadeposito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='empresa.cuentas_bancarias')),
                ('cxcuentatransferencia', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='clientes.cuentas_bancarias')),
                ('cxtipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='empresa.tipos_factoring')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recuperaciones_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nsaldoaldia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nvalorrecuperacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nvalorbaja', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsaldoaldiabajacobranza', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nvalorbajacobranza', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ndiasacondonar', models.SmallIntegerField(default=0, null=True)),
                ('chequeprotestado', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cobranzas.cheques_protestados')),
                ('cxusuariocondona', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('documentoprotestado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobranzas.documentos_protestados')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('recuperacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobranzas.recuperaciones_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Liquidacion_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nvaloraplicado', models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True)),
                ('cxtipooperacion', models.CharField(choices=[('R', 'Recuperación'), ('C', 'Cobranzas'), ('L', 'Liquidación'), ('D', 'Debito bancario')], max_length=1)),
                ('operacion', models.BigIntegerField()),
                ('cargo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='operaciones.cargos_detalle')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('liquidacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liquidacion_detalle', to='cobranzas.liquidacion_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documentos_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nvalorcobranza', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nvalorbaja', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nretenciones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nsaldoaldia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ndiasacondonar', models.SmallIntegerField(default=0)),
                ('accesorioquitado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.chequesaccesorios')),
                ('cxcobranza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobranzas.documentos_cabecera')),
                ('cxdocumento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.documentos')),
                ('cxusuariocondona', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuariocondona', to=settings.AUTH_USER_MODEL)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DebitosCuentasConjuntas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('dmovimiento', models.DateField()),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ctmotivo', models.CharField(max_length=60)),
                ('cxtipooperacion', models.CharField(choices=[('R', 'Recuperación'), ('C', 'Cobranzas')], max_length=1, null=True)),
                ('operacion', models.BigIntegerField(null=True)),
                ('cuentabancaria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuentasconjuntas.cuentas_bancarias')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('notadedebito', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='debito_cuentaconjunta', to='operaciones.notas_debito_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cargos_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nsaldoaldia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('nvalorcobranza', models.DecimalField(decimal_places=2, max_digits=10)),
                ('jcargos', models.JSONField()),
                ('cxcobranza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobranzas.cargos_cabecera')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('notadedebito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.notas_debito_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxcheque',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cheque_cobranza_cargos', to='cobranzas.cheques'),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxcliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_cobranza_cargos', to='clientes.datos_generales'),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxcuentadeposito',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='banco_deposito_cargos', to='empresa.cuentas_bancarias'),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxcuentatransferencia',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='clientes.cuentas_bancarias'),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxtipofactoring',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tipofactoring_cobranza_cargos', to='empresa.tipos_factoring'),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='cxusuariocrea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cargos_cabecera',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
        ),
    ]
