# Generated by Django 4.0.4 on 2023-09-27 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0025_remove_anexos_ctrutageneracion'),
    ]

    operations = [
        migrations.AddField(
            model_name='anexos',
            name='cxtipocliente',
            field=models.CharField(choices=[('N', 'Natural'), ('J', 'Jurídico'), ('T', 'Todos')], default='J', help_text='tipo de cliente: natural , jurídico, todos', max_length=1),
        ),
    ]