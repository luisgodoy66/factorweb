# Generated by Django 4.0.4 on 2022-05-11 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0002_alter_datos_participantes_ctcelular_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_participantes',
            name='ctdireccion',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='datos_participantes',
            name='ctemail',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='datos_participantes',
            name='ctgirocomercial',
            field=models.TextField(null=True),
        ),
    ]
