# Generated by Django 4.0.4 on 2023-09-20 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0023_alter_anexos_fanexo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexos',
            name='fanexo',
            field=models.FileField(blank=True, upload_to='anexos/'),
        ),
    ]
