# Generated by Django 4.0.4 on 2023-08-29 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pais', '0003_actividades'),
        ('empresa', '0009_alter_tipos_factoring_ctinicialesasignacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datos_participantes',
            name='cxactividad',
        ),
        migrations.AddField(
            model_name='datos_participantes',
            name='actividad',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, to='pais.actividades'),
        ),
    ]
