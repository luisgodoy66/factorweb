# Generated by Django 4.0.4 on 2022-06-10 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0012_remove_documentos_nivacargado'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='nplazo',
            field=models.IntegerField(default=0),
        ),
    ]
