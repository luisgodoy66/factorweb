# Generated by Django 4.2.5 on 2024-12-26 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bases', '0011_alter_empresas_ctnombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresas',
            name='ilogocorto',
            field=models.ImageField(blank=True, default='logo2.png', null=True, upload_to='static/factorweb/imagenes/logo/'),
        ),
        migrations.AddField(
            model_name='empresas',
            name='ilogolargo',
            field=models.ImageField(blank=True, default='logo1.png', null=True, upload_to='static/factorweb/imagenes/logo/'),
        ),
        migrations.AddField(
            model_name='empresas',
            name='nporcentajeiva',
            field=models.DecimalField(decimal_places=2, default=15, max_digits=5),
        ),
    ]