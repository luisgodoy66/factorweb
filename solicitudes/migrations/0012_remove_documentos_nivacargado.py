# Generated by Django 4.0.4 on 2022-06-03 22:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0011_documentos_ntasacomision'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentos',
            name='nivacargado',
        ),
    ]
