# Generated by Django 4.0.4 on 2023-01-24 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentasconjuntas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimientos',
            name='cxmovimiento',
        ),
        migrations.AddField(
            model_name='movimientos',
            name='movimiento',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Debitos',
        ),
    ]
