# Generated by Django 4.0.4 on 2023-09-20 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0022_remove_anexos_ctrutaanexo_anexos_fanexo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexos',
            name='fanexo',
            field=models.FileField(blank=True, upload_to='static/factorweb/anexos/'),
        ),
    ]
