# Generated by Django 4.0.4 on 2023-02-13 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0019_remove_datos_participantes_cxlocalidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasas_factoring',
            name='ctinicialesentablas',
            field=models.CharField(max_length=4, null=True),
        ),
    ]
