# Generated by Django 4.0.4 on 2023-07-15 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bases', '0005_empresas_ctciudad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresas',
            name='ctcontribuyenteespecial',
            field=models.CharField(default='0000', max_length=4, null=True),
        ),
    ]
