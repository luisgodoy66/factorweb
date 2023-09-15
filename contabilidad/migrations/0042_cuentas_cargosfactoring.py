# Generated by Django 4.0.4 on 2023-08-07 22:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bases', '0006_alter_empresas_ctcontribuyenteespecial'),
        ('empresa', '0007_tipos_factoring_lgenerafacturaenaceptacion'),
        ('operaciones', '0018_movimientos_maestro_lcargo'),
        ('contabilidad', '0041_cuentas_especiales_comisionchequesprotestados'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuentas_cargosfactoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cargo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cuenta_cargo', to='operaciones.movimientos_maestro')),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='contabilidad.plan_cuentas')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
                ('tipofactoring', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cuenta_cargotipofactoring', to='empresa.tipos_factoring')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]