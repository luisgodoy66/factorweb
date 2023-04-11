# Generated by Django 4.0.4 on 2023-04-11 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bases', '0001_initial'),
        ('cuentasconjuntas', '0006_rename_movimiento_movimientos_cxmovimiento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuentas_bancarias',
            name='empresa',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimientos',
            name='empresa',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transferencias',
            name='empresa',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_empresa', to='bases.empresas'),
            preserve_default=False,
        ),
    ]
