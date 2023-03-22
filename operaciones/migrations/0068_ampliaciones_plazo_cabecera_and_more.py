# Generated by Django 4.0.4 on 2023-03-13 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operaciones', '0067_alter_asignacion_ddesembolso'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ampliaciones_plazo_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxampliacion', models.CharField(max_length=10)),
                ('dampliacionhasta', models.DateField()),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('notadedebito', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='operaciones.notas_debito_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ampliaciones_plazo_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('dampliaciondesde', models.DateField()),
                ('ampliacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.ampliaciones_plazo_cabecera')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='operaciones.documentos')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
