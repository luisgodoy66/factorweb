# Generated by Django 4.0.4 on 2022-11-29 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0034_recuperaciones_detalle_nsaldoaldiabajacobranza'),
    ]

    operations = [
        migrations.AddField(
            model_name='cheques_protestados',
            name='cxtipooperacion',
            field=models.CharField(default='C', max_length=1),
            preserve_default=False,
        ),
    ]
