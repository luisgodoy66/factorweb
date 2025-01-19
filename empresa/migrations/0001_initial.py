# Generated by Django 4.0.4 on 2023-04-15 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bases', '0001_initial'),
        ('pais', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tipos_factoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtipofactoring', models.CharField(max_length=3)),
                ('cttipofactoring', models.CharField(max_length=40)),
                ('ctabreviacion', models.CharField(max_length=30)),
                ('cxmoneda', models.CharField(max_length=3)),
                ('nvalorminimopordocumento', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('lmanejalineafactoring', models.BooleanField(default=True)),
                ('lanticipatotalnegociado', models.BooleanField(default=False)),
                ('ndiasgracia', models.IntegerField(default=5)),
                ('lpermitediasferiados', models.BooleanField(default=False)),
                ('lmanejacondicionesoperativas', models.BooleanField(default=True)),
                ('lcargagaoa', models.BooleanField(default=True)),
                ('lgeneradcenaceptacion', models.BooleanField(default=True)),
                ('lgeneragaoenaceptacion', models.BooleanField(default=True)),
                ('lesnegociada', models.BooleanField(default=True)),
                ('lcobramorabc', models.BooleanField(default=False)),
                ('nporcentajeretencionenfactura', models.DecimalField(decimal_places=2, default=0, max_digits=5, null=True)),
                ('ctinicialesliquidacioncobranza', models.CharField(blank=True, max_length=3)),
                ('lacumulagaoaatasagao', models.BooleanField(default=False)),
                ('lfactoringproveedores', models.BooleanField(default=False)),
                ('ctinicialesasignacion', models.CharField(blank=True, max_length=3, null=True)),
                ('lcargadcenampliacionplazo', models.BooleanField(default=False)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tipos_documentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtipodocumento', models.CharField(max_length=1)),
                ('cttipodocumento', models.CharField(max_length=15)),
                ('ctabreviacion', models.CharField(blank=True, max_length=5)),
                ('lprincipal', models.BooleanField(default=True)),
                ('laccesorio', models.BooleanField(default=False)),
                ('lefectocobro', models.BooleanField(default=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tasas_factoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtasa', models.CharField(max_length=4)),
                ('cttasa', models.CharField(blank=True, max_length=60)),
                ('lflat', models.BooleanField(default=False)),
                ('ndiasperiocidad', models.DecimalField(decimal_places=0, default=0, max_digits=3)),
                ('ctdescripcionenreporte', models.TextField(blank=True)),
                ('limprimeenreporte', models.BooleanField(default=False)),
                ('lcargaiva', models.BooleanField(default=True)),
                ('lsobreanticipo', models.BooleanField(default=True)),
                ('ctinicialesentablas', models.CharField(max_length=4, null=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Localidades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('ctlocalidad', models.CharField(blank=True, max_length=80)),
                ('lactiva', models.BooleanField(default=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Funcionarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxfuncionario', models.CharField(max_length=5)),
                ('ctfuncionario', models.CharField(max_length=100)),
                ('nporcentajecomision', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('lcomisionflat', models.BooleanField()),
                ('nperiocidadcomision', models.DecimalField(decimal_places=2, default=360, max_digits=5)),
                ('lcomisionsobregao', models.BooleanField(default=False)),
                ('lcomisionsobredescuentocartera', models.BooleanField(default=False)),
                ('lcomisionsobrecartera', models.BooleanField(default=False)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Datos_participantes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtipoid', models.CharField(choices=[('C', 'CEDULA'), ('R', 'RUC'), ('P', 'PASAPORTE'), ('O', 'OTRO')], max_length=1)),
                ('cxparticipante', models.CharField(max_length=13, unique=True)),
                ('ctnombre', models.CharField(max_length=100)),
                ('cxzona', models.CharField(max_length=5, null=True)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('ctdireccion', models.TextField(null=True)),
                ('ctemail', models.EmailField(max_length=254, null=True)),
                ('ctemail2', models.EmailField(blank=True, max_length=254, null=True)),
                ('cttelefono1', models.CharField(blank=True, max_length=30, null=True)),
                ('cttelefono2', models.CharField(blank=True, max_length=30, null=True)),
                ('ctcelular', models.CharField(blank=True, max_length=30, null=True)),
                ('ctgirocomercial', models.TextField(null=True)),
                ('cxactividad', models.CharField(help_text='actividad comercial segun código ciiu', max_length=10, null=True)),
                ('dinicioactividades', models.DateField(help_text='fecha de inicio de actividades', null=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cuentas_bancarias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxcuenta', models.CharField(max_length=20)),
                ('ncheque', models.IntegerField(null=True)),
                ('lformatopreimpreso', models.BooleanField(default=False)),
                ('limprimecheque', models.BooleanField(default=False)),
                ('lactiva', models.BooleanField(default=True)),
                ('ctrutaarchivobanco', models.TextField(null=True)),
                ('cxciabco', models.CharField(max_length=5, null=True)),
                ('cxbanco', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='pais.bancos')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtransaccion', models.CharField(max_length=20)),
                ('nultimonumero', models.IntegerField(default=0)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Configuracion_correos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxtipo', models.CharField(choices=[('FEL', 'FACTURACION ELECTRONICA'), ('CRM', 'CLIENTES')], max_length=3)),
                ('ctservidorcorreosaliente', models.TextField(default='smtp.gmail.com')),
                ('npuerto', models.IntegerField(default=587)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Clases_cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxclase', models.CharField(max_length=3)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
