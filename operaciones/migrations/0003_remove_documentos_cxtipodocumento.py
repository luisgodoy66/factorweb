# Generated by Django 4.0.4 on 2023-04-19 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0002_alter_datos_operativos_cxcliente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentos',
            name='cxtipodocumento',
        ),
    ]