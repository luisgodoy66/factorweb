# Generated by Django 4.0.4 on 2023-05-27 23:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bases', '0003_empresas_cxusuariomodifica_empresas_dmodificacion'),
        ('empresa', '0003_alter_datos_participantes_cxparticipante'),
    ]

    operations = [
        migrations.CreateModel(
            name='Puntos_emision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxestablecimiento', models.CharField(max_length=3)),
                ('cxpuntoemision', models.CharField(max_length=3)),
                ('ctdireccion', models.TextField()),
                ('lgeneracionxmldocumentoelectronico', models.BooleanField(default=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]