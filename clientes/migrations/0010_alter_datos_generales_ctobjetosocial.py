# Generated by Django 4.0.4 on 2022-05-13 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0009_alter_datos_generales_ctbeneficiariodevolucion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_generales',
            name='ctobjetosocial',
            field=models.TextField(),
        ),
    ]
