# Generated by Django 4.0.4 on 2022-05-26 03:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('solicitudes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxcliente', models.CharField(max_length=13, unique=True)),
                ('ctnombre', models.CharField(max_length=100)),
                ('cxzona', models.CharField(max_length=5, null=True)),
                ('cxlocalidad', models.CharField(max_length=4, null=True)),
                ('ctdireccion', models.TextField(null=True)),
                ('ctemail', models.EmailField(max_length=254, null=True)),
                ('ctemail2', models.EmailField(blank=True, max_length=254, null=True)),
                ('cttelefono1', models.CharField(blank=True, max_length=30, null=True)),
                ('cttelefono2', models.CharField(blank=True, max_length=30, null=True)),
                ('ctcelular', models.CharField(blank=True, max_length=30, null=True)),
                ('ctgirocomercial', models.TextField(null=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='cxcliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cliente_asignacion', to='solicitudes.clientes'),
        ),
    ]
