# Generated by Django 4.0.4 on 2023-06-13 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0014_remove_desembolsos_cxasientodiario_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movimientos_maestro',
            old_name='lcargo',
            new_name='litemfactura',
        ),
    ]
