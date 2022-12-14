# Generated by Django 4.0.4 on 2022-06-28 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operaciones', '0023_alter_asignacion_cxasignacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='nvalornonegociado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name='ChequesAccesorios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxbanco', models.CharField(max_length=3)),
                ('cxcuenta', models.CharField(max_length=15)),
                ('ctcheque', models.CharField(max_length=13)),
                ('ctgirador', models.CharField(max_length=60)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('nvalor', models.DecimalField(decimal_places=2, max_digits=15)),
                ('demision', models.DateTimeField()),
                ('dvencimiento', models.DateTimeField()),
                ('nporcentajeanticipo', models.DecimalField(decimal_places=2, max_digits=5)),
                ('ntasadescuento', models.DecimalField(decimal_places=8, max_digits=11)),
                ('ntasacomision', models.DecimalField(decimal_places=8, max_digits=11)),
                ('lcanjeado', models.BooleanField(default=False)),
                ('ddeposito', models.DateTimeField(null=True)),
                ('cxusuariocrea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_usuariocrea', to=settings.AUTH_USER_MODEL)),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operaciones.documentos')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
