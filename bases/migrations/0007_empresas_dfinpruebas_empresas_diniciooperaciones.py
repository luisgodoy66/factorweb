# Generated by Django 4.0.4 on 2023-08-26 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bases', '0006_alter_empresas_ctcontribuyenteespecial'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresas',
            name='dfinpruebas',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='empresas',
            name='diniciooperaciones',
            field=models.DateField(null=True),
        ),
    ]
