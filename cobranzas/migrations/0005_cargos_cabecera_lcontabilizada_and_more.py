# Generated by Django 4.0.4 on 2023-07-01 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0004_liquidacion_cabecera_ndescuentodecarteravencido'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargos_cabecera',
            name='lcontabilizada',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='documentos_cabecera',
            name='lcontabilizada',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='recuperaciones_cabecera',
            name='lcontabilizada',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='cxestado',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
