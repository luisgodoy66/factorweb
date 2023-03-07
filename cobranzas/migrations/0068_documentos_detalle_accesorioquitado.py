# Generated by Django 4.0.4 on 2023-03-06 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0064_chequesaccesorios_laccesorioquitado_cheques_quitados_and_more'),
        ('cobranzas', '0067_alter_documentos_cabecera_dcobranza'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos_detalle',
            name='accesorioquitado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='operaciones.chequesaccesorios'),
        ),
    ]