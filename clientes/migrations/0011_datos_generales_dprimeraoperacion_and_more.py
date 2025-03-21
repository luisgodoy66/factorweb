# Generated by Django 5.1.5 on 2025-03-20 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0010_alter_cupos_compradores_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datos_generales',
            name='dprimeraoperacion',
            field=models.DateField(help_text='fecha de la primera operación', null=True),
        ),
        migrations.AddField(
            model_name='datos_generales',
            name='ncantidadoperaciones',
            field=models.SmallIntegerField(default=0, help_text='cantidad de operaciones realizadas'),
        ),
    ]
