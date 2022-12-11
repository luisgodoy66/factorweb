# Generated by Django 4.0.4 on 2022-10-06 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cobranzas', '0004_documentos_cabecera_ldepositoencuentaconjunta_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cheques',
            name='cxcheque',
        ),
        migrations.RemoveField(
            model_name='cheques',
            name='demision',
        ),
        migrations.AddField(
            model_name='cheques',
            name='ctplaza',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='documentos_cabecera',
            name='cxcheque',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.RESTRICT, to='cobranzas.cheques'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cheques',
            name='ctgirador',
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='cheques',
            name='cxtipoparticipante',
            field=models.CharField(choices=[('D', 'Deudor'), ('C', 'Cliente')], max_length=1),
        ),
    ]
