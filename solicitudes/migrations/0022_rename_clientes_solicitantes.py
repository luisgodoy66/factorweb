"""Renombra el modelo Clientes de la app solicitudes a Solicitantes.

El registro representa a la empresa que *solicita* factoring y que no
necesariamente llega a ser cliente del factor, por lo que el nombre del modelo
se alinea con el dominio (solicitante) y con la promoción posterior a
clientes.Datos_generales.

Ademas del renombrado de la tabla se renombran los permisos de
django.contrib.auth, de modo que los permisos ya asignados a usuarios y grupos
(solicitudes.add_clientes, view_clientes, ...) sigan siendo validos sobre el
modelo renombrado.

El ContentType no se toca aqui: Django inyecta un RenameContentType despues de
cada RenameModel (contenttypes.management.inject_rename_contenttypes_operations),
asi que al ejecutarse este RunPython el content type ya se llama
'solicitantes' y lo unico pendiente es renombrar los codenames heredados.
"""
from django.db import migrations, models

# codename viejo -> (codename nuevo, nombre para el admin)
PERMISOS = {
    'add_clientes': ('add_solicitantes', 'Can add Solicitante'),
    'change_clientes': ('change_solicitantes', 'Can change Solicitante'),
    'delete_clientes': ('delete_solicitantes', 'Can delete Solicitante'),
    'view_clientes': ('view_solicitantes', 'Can view Solicitante'),
}


def _renombrar_permisos(apps, model_viejo, model_nuevo, permisos):
    """Renombra los permisos heredados del modelo.

    `model_nuevo` es el nombre que tiene el ContentType en este punto de la
    migracion y `model_viejo` el de los codenames que hay que reemplazar.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')

    ct_nuevo = ContentType.objects.filter(
        app_label='solicitudes', model=model_nuevo).first()
    ct_viejo = ContentType.objects.filter(
        app_label='solicitudes', model=model_viejo).first()

    if ct_nuevo is None and ct_viejo is None:
        # base nueva: post_migrate creara los permisos ya con el nombre nuevo
        return

    if ct_nuevo is None:
        # el RenameContentType automatico no se aplico (p. ej. porque ya
        # existia un content type con el nombre nuevo): se renombra aqui.
        ct_viejo.model = model_nuevo
        ct_viejo.save(update_fields=['model'])
        ct_nuevo, ct_viejo = ct_viejo, None

    if ct_viejo is not None and ct_viejo.pk != ct_nuevo.pk:
        # content type obsoleto: trasladar sus permisos al vigente
        for codigo_viejo, (codigo_nuevo, nombre) in permisos.items():
            Permission.objects.filter(
                content_type=ct_nuevo, codename=codigo_nuevo).delete()
            Permission.objects.filter(
                content_type=ct_nuevo, codename=codigo_viejo).delete()
            Permission.objects.filter(
                content_type=ct_viejo, codename=codigo_viejo).update(
                    content_type=ct_nuevo, codename=codigo_nuevo, name=nombre)
        Permission.objects.filter(content_type=ct_viejo).delete()
        ct_viejo.delete()

    for codigo_viejo, (codigo_nuevo, nombre) in permisos.items():
        # se descarta un permiso homonimo ya creado (p. ej. por post_migrate)
        # para no violar la restriccion unica (content_type, codename)
        Permission.objects.filter(
            content_type=ct_nuevo, codename=codigo_nuevo).delete()
        Permission.objects.filter(
            content_type=ct_nuevo, codename=codigo_viejo).update(
                codename=codigo_nuevo, name=nombre)


def renombrar_a_solicitantes(apps, schema_editor):
    _renombrar_permisos(apps, 'clientes', 'solicitantes', PERMISOS)


def renombrar_a_clientes(apps, schema_editor):
    inversos = {nuevo: (viejo, nombre.replace('Solicitante', 'clientes'))
                for viejo, (nuevo, nombre) in PERMISOS.items()}
    _renombrar_permisos(apps, 'solicitantes', 'clientes', inversos)


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0021_liquidacion_notificada'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Clientes',
            new_name='Solicitantes',
        ),
        migrations.AlterModelOptions(
            name='solicitantes',
            options={
                'ordering': ['ctnombre'],
                'verbose_name': 'Solicitante',
                'verbose_name_plural': 'Solicitantes',
            },
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='cxcliente',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='solicitante_asignacion',
                to='solicitudes.solicitantes',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='solicitantes',
            name='cliente_solicitud',
        ),
        migrations.AddConstraint(
            model_name='solicitantes',
            constraint=models.UniqueConstraint(
                fields=('cxcliente', 'empresa'), name='solicitante_solicitud'),
        ),
        migrations.RunPython(
            renombrar_a_solicitantes, renombrar_a_clientes),
    ]
