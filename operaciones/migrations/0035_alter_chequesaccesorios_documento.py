# Generated by Django 4.0.4 on 2022-10-18 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0034_alter_asignacion_cxestado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chequesaccesorios',
            name='documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documento_cheque', to='operaciones.documentos'),
        ),
    ]
