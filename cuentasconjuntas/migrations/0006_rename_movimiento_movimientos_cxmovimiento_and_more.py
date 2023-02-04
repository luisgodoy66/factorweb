# Generated by Django 4.0.4 on 2023-01-26 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0017_alter_cuentas_bancarias_ctrutaarchivobanco_and_more'),
        ('cuentasconjuntas', '0005_alter_movimientos_dmovimiento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movimientos',
            old_name='movimiento',
            new_name='cxmovimiento',
        ),
        migrations.AlterField(
            model_name='transferencias',
            name='cuentadestino',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='banco_destino', to='empresa.cuentas_bancarias'),
        ),
    ]