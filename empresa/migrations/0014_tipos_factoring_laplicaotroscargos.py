# Generated by Django 4.0.4 on 2024-07-10 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0013_otros_cargos'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipos_factoring',
            name='laplicaotroscargos',
            field=models.BooleanField(default=False),
        ),
    ]