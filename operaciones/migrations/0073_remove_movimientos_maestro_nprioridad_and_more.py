# Generated by Django 4.0.4 on 2023-04-09 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0072_chequesaccesorios_ncontadorprorrogas_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimientos_maestro',
            name='nprioridad',
        ),
        migrations.AddField(
            model_name='movimientos_maestro',
            name='lcargo',
            field=models.BooleanField(default=False),
        ),
    ]
