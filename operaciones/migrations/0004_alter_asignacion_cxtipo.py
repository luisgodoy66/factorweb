# Generated by Django 4.0.4 on 2022-05-26 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0003_asignacion_alter_datos_operativos_ntasacomision_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='cxtipo',
            field=models.CharField(choices=[('A', 'Con accesorios'), ('P', 'Facturas puras')], max_length=1),
        ),
    ]
