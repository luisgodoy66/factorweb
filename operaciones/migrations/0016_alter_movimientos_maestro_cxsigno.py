# Generated by Django 4.0.4 on 2022-06-13 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0015_remove_movimientos_clientes_cxaño_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientos_maestro',
            name='cxsigno',
            field=models.CharField(choices=[('+', 'Suma'), ('-', 'Resta')], max_length=1),
        ),
    ]
