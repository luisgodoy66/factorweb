# Generated by Django 4.0.4 on 2023-03-02 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0026_remove_asignacion_cxasignacion_asignacion_asignacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='chequesaccesorios',
            name='cxpropietariocuenta',
            field=models.CharField(choices=[('C', 'Cliente'), ('D', 'Deudor')], default='D', max_length=1),
        ),
    ]