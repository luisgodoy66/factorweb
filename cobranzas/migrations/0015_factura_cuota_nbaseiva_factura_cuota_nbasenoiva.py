# Generated by Django 4.0.4 on 2024-08-05 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0014_factura_cuota'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura_cuota',
            name='nbaseiva',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='factura_cuota',
            name='nbasenoiva',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
