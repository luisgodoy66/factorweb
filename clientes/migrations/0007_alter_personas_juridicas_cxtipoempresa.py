# Generated by Django 4.0.4 on 2023-10-05 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0006_datos_operativos_hist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cxtipoempresa',
            field=models.CharField(choices=[('ANO', 'Anónima'), ('LTD', 'Resposabilidad Limitada'), ('SAS', 'Por acciones simplificadas'), ('COL', 'Nombre colectivo'), ('SIM', 'En comandita simple'), ('MIX', 'Economía mixta')], help_text='Anonima, limitada, etc.', max_length=3),
        ),
    ]