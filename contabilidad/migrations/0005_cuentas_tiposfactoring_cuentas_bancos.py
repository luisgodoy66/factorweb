# Generated by Django 4.0.4 on 2023-05-23 12:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('empresa', '0003_alter_datos_participantes_cxparticipante'),
        ('bases', '0001_initial'),
        ('pais', '0001_initial'),
        ('contabilidad', '0004_rename_cxcuentaconjunta_cuentas_especiales_cuentaconjunta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuentas_tiposfactoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='contabilidad.plan_cuentas')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('tipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='empresa.tipos_factoring')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cuentas_bancos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('banco', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cuenta_banco', to='pais.bancos')),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='contabilidad.plan_cuentas')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
