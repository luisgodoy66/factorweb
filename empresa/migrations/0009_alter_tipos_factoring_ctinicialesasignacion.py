# Generated by Django 4.0.4 on 2023-08-28 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0008_remove_tipos_factoring_cxtipofactoring'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipos_factoring',
            name='ctinicialesasignacion',
            field=models.CharField(blank=True, default='OP-', max_length=3),
        ),
    ]