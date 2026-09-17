from django.db import migrations


def cifrar_passwords_existentes(apps, schema_editor):
    """Re-guarda cada registro para que ctpasswordcorreo quede cifrado con Fernet.

    Al leer, from_db_value ya intent\u00f3 desencriptar (o dej\u00f3 el texto plano heredado
    tal cual si no era un token v\u00e1lido); al guardar, get_prep_value lo cifra de nuevo.
    """
    Configuracion_correos = apps.get_model('empresa', 'Configuracion_correos')
    for registro in Configuracion_correos.objects.all():
        if not registro.ctpasswordcorreo:
            continue
        registro.save(update_fields=['ctpasswordcorreo'])


def revertir(apps, schema_editor):
    pass  # no se puede recuperar el texto plano original de forma segura


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0025_alter_configuracion_correos_ctpasswordcorreo'),
    ]

    operations = [
        migrations.RunPython(cifrar_passwords_existentes, revertir),
    ]
