# Generated by Django 4.0.4 on 2022-06-13 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0013_alter_cargos_detalle_cxasignacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='ctbancochequegarantia',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='ctcuentachequegarantia',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='ctnumerochequegarantia',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='cxlocalidad',
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
