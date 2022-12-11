# Generated by Django 4.0.4 on 2022-11-19 20:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0044_remove_datos_generales_ctbeneficiarioliquidacionasignacion_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('empresa', '0017_alter_cuentas_bancarias_ctrutaarchivobanco_and_more'),
        ('operaciones', '0042_alter_cargos_detalle_cxasignacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notas_debito_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('dnotadebito', models.DateField()),
                ('cxnotadebito', models.CharField(max_length=10, unique=True)),
                ('nvalor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('nsaldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cxtipooperacion', models.CharField(choices=[('L', 'Liquidación'), ('C', 'Cobranzas')], max_length=1)),
                ('operacion', models.BigIntegerField()),
                ('cxcliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='clientes.datos_generales')),
                ('cxtipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empresa.tipos_factoring', to_field='cxtipofactoring')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notas_debito_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cargo', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='operaciones.cargos_detalle')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('notadebito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.notas_debito_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
