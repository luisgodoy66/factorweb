# Generated by Django 4.0.4 on 2023-01-24 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentasconjuntas', '0003_movimientos_dmovimiento_transferencias_dmovimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferencias',
            name='dmovimiento',
            field=models.DateField(),
        ),
    ]
