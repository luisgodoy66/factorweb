# Generated by Django 4.0.4 on 2022-12-07 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0044_liquidacion_detalle_nvaloraplicado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liquidacion_detalle',
            name='nvaloraplicado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
