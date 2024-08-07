# Generated by Django 4.0.4 on 2024-07-27 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0030_asignacion_jotroscargos_asignacion_nbaseiva_and_more'),
        ('cobranzas', '0010_liquidacion_cabecera_jotroscargos_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pagare_cabecera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcobranza', models.DateField(auto_created=True)),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('cxcobranza', models.CharField(max_length=8)),
                ('cxformapago', models.CharField(choices=[('EFE', 'Efectivo'), ('CHE', 'Cheque'), ('MOV', 'Movimiento contable'), ('TRA', 'Transferencia'), ('DEP', 'Deposito de accesorio')], max_length=3)),
                ('nvalor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cxestado', models.CharField(default='A', max_length=1)),
                ('ddeposito', models.DateTimeField(null=True)),
                ('lcontabilizada', models.BooleanField(default=False, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pagare_detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dregistro', models.DateTimeField(auto_now_add=True)),
                ('dmodificacion', models.DateTimeField(auto_now=True)),
                ('cxusuariomodifica', models.IntegerField(blank=True, null=True)),
                ('leliminado', models.BooleanField(default=False)),
                ('cxusuarioelimina', models.IntegerField(blank=True, null=True)),
                ('nvalorcobranza', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nsaldoaldia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('accesorioquitado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.chequesaccesorios')),
                ('cobranza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobranzas.pagare_cabecera')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
