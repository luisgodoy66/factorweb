# Generated by Django 4.0.4 on 2023-08-29 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pais', '0003_actividades'),
        ('empresa', '0010_remove_datos_participantes_cxactividad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_participantes',
            name='actividad',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='pais.actividades'),
        ),
    ]