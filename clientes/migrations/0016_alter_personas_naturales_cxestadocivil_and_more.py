# Generated by Django 4.0.4 on 2022-05-20 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0015_alter_personas_naturales_dnacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personas_naturales',
            name='cxestadocivil',
            field=models.CharField(choices=[('S', 'Soltero'), ('C', 'Casado'), ('V', 'Viudo'), ('D', 'Divorciado'), ('U', 'Unión libre')], max_length=3),
        ),
        migrations.AlterField(
            model_name='personas_naturales',
            name='cxsexo',
            field=models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1),
        ),
        migrations.AlterField(
            model_name='personas_naturales',
            name='dnacimiento',
            field=models.DateField(default='2000-01-01', null=True),
        ),
    ]
