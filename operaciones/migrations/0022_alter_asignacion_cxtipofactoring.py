# Generated by Django 4.0.4 on 2022-06-16 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0015_alter_tipos_factoring_ctinicialesasignacion'),
        ('operaciones', '0021_condiciones_operativas_cabecera_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='cxtipofactoring',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tipofactoring_asignacion', to='empresa.tipos_factoring', to_field='cxtipofactoring'),
        ),
    ]
