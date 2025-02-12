# Generated by Django 5.1.5 on 2025-02-10 16:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bases', '0016_alter_empresas_ilogolargo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuracion_slack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('ctdescripcion', models.CharField(max_length=100)),
                ('ctslackbottoken', models.CharField(max_length=100)),
                ('ctslackchannelname', models.CharField(max_length=50)),
                ('ctslacksigningsecret', models.CharField(max_length=100)),
                ('lactivo', models.BooleanField(default=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
