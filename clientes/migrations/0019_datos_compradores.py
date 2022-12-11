# Generated by Django 4.0.4 on 2022-06-04 18:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0013_alter_tasas_factoring_cttasa'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientes', '0018_alter_datos_generales_cxcliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Datos_compradores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxactividad', models.CharField(help_text='actividad comercial segun codigo ciiu', max_length=10, null=True)),
                ('ctemailfacturacionelectronica', models.EmailField(help_text='direccion email para factracion electronica', max_length=254, null=True)),
                ('cxcomprador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datos_generales_comprador', to='empresa.datos_participantes', to_field='cxparticipante')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
