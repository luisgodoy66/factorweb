# Generated by Django 4.0.4 on 2023-05-01 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0004_alter_asignacion_cxcliente_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ampliaciones_plazo_cabecera',
            name='notadedebito',
        ),
        migrations.AddField(
            model_name='ampliaciones_plazo_cabecera',
            name='nvalor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]