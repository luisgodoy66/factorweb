# Generated by Django 4.0.4 on 2022-09-09 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0038_remove_personas_juridicas_dinicioactividades_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datos_compradores',
            name='ctemailfacturacionelectronica',
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='ctcargorepresentante2',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='ctcargorepresentante3',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='ctrepresentante2',
            field=models.TextField(blank=True, help_text='Nombre de segundo representante', null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='ctrepresentante3',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cttelefonorepresentante2',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cttelefonorepresentante3',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cxestadocivilrepresentante2',
            field=models.CharField(blank=True, choices=[('S', 'Soltero'), ('C', 'Casado'), ('U', 'unión libre'), ('D', 'Divorciado')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cxestadocivilrepresentante3',
            field=models.CharField(blank=True, choices=[('S', 'Soltero'), ('C', 'Casado'), ('U', 'unión libre'), ('D', 'Divorciado')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cxrepresentante2',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='cxrepresentante3',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='dvencimientocargorepresentante2',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personas_juridicas',
            name='dvencimientocargorepresentante3',
            field=models.DateField(blank=True, null=True),
        ),
    ]
