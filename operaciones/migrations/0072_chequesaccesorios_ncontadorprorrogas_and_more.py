# Generated by Django 4.0.4 on 2023-03-22 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0071_remove_ampliaciones_plazo_cabecera_cxampliacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chequesaccesorios',
            name='ncontadorprorrogas',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='chequesaccesorios',
            name='ndiasprorroga',
            field=models.SmallIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='documentos',
            name='ncontadorprorrogas',
            field=models.SmallIntegerField(default=0),
        ),
    ]
