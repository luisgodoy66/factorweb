# Generated by Django 4.0.4 on 2023-09-21 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0024_alter_anexos_fanexo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anexos',
            name='ctrutageneracion',
        ),
    ]