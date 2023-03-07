# Generated by Django 4.0.4 on 2023-03-06 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0049_alter_datos_compradores_cxestado'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operaciones', '0063_chequesaccesorios_ncanjeadopor'),
    ]

    operations = [
        migrations.AddField(
            model_name='chequesaccesorios',
            name='laccesorioquitado',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Cheques_quitados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('nsaldo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ctmotivoquitado', models.CharField(max_length=60)),
                ('dultimacobranza', models.DateTimeField(null=True)),
                ('cxcliente', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='clientes.datos_generales', to_field='cxcliente')),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='chequesaccesorios',
            name='chequequitado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.cheques_quitados'),
        ),
    ]
