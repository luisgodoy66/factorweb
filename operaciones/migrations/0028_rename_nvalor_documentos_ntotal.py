# Generated by Django 4.0.4 on 2022-08-07 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0027_chequesaccesorios_nanticipo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentos',
            old_name='nvalor',
            new_name='ntotal',
        ),
    ]
