# Generated by Django 4.0.4 on 2023-06-13 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0003_liquidacion_cabecera_nporcentajeiva'),
    ]

    operations = [
        migrations.AddField(
            model_name='liquidacion_cabecera',
            name='ndescuentodecarteravencido',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
