"""Autenticacion de webhooks entrantes mediante claves por empresa.

Cada empresa (tenant) puede tener varias claves en `empresa.Claves_webhook`.
Las claves se guardan solo como hash (make_password/check_password) y se
identifican por un prefijo de 8 caracteres, de modo que la verificacion no
recorre la tabla completa.

El resultado de la validacion es la EMPRESA DUENA DE LA CLAVE. Los endpoints
deben usar esa empresa como filtro y descartar cualquier `empresa_id` que
venga en el cuerpo de la peticion: de lo contrario un cliente podria leer los
datos de otro simplemente cambiando ese campo.
"""
import logging

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import DatabaseError

logger = logging.getLogger(__name__)

# Nombres de cabecera aceptados para transportar la clave.
NOMBRES_CABECERA_CLAVE = ('X-Margarita-Key', 'X-Margarita-API-Key')

# Longitud del prefijo almacenado en Claves_webhook.ctprefijo.
LONGITUD_PREFIJO = 8

# Motivo devuelto cuando la empresa es valida pero autenticada con la clave
# global de entorno en lugar de una clave propia de la empresa.
MOTIVO_CLAVE_GLOBAL = 'clave global de entorno'


def obtener_clave_de_peticion(request):
    """Extrae la clave enviada, admitiendo los dos nombres de cabecera."""
    for nombre in NOMBRES_CABECERA_CLAVE:
        valor = request.headers.get(nombre)
        if valor:
            return valor.strip()
    valor = request.POST.get('api_key')
    return valor.strip() if valor else ''


def _clave_global_valida(clave_presentada):
    """Comprueba la clave global de entorno (compatibilidad hacia atras)."""
    clave_global = getattr(settings, 'INTERNAL_API_KEY', None) or \
        getattr(settings, 'MARGARITA_API_KEY', None)
    if not clave_global:
        return False
    from hmac import compare_digest
    return compare_digest(str(clave_global), str(clave_presentada))


def validar_clave_webhook(request):
    """Valida la clave del webhook.

    Devuelve una tupla (empresa_id, clave_usada, error):
      - empresa_id : id de la empresa duena de la clave, o None si es invalida
      - clave_usada : instancia de Claves_webhook, o None si se uso la global
      - error      : mensaje descriptivo cuando no se pudo autenticar
    """
    clave_presentada = obtener_clave_de_peticion(request)
    if not clave_presentada:
        return None, None, 'falta la cabecera %s' % ' / '.join(NOMBRES_CABECERA_CLAVE)

    # Import local: evita cargar los modelos de empresa al importar este modulo.
    from .models import Claves_webhook

    # 1. Buscar candidatas por prefijo. Un prefijo vacio no permite filtrar.
    candidatas = []
    if len(clave_presentada) >= LONGITUD_PREFIJO:
        prefijo = clave_presentada[:LONGITUD_PREFIJO]
        try:
            candidatas = list(
                Claves_webhook.objects
                .filter(ctprefijo=prefijo, lactiva=True, leliminado=False)
                .select_related('empresa')
            )
        except DatabaseError:
            logger.exception('Error consultando claves de webhook por prefijo')
            candidatas = []

    # 2. Verificar el hash de cada candidata vigente.
    for clave in candidatas:
        if not clave.esta_vigente():
            continue
        if not clave.ctclavehash:
            continue
        try:
            coincide = check_password(clave_presentada, clave.ctclavehash)
        except (ValueError, TypeError):
            # Hash con formato no reconocido: se ignora esta candidata.
            continue
        if coincide:
            try:
                clave.registrar_uso()
            except DatabaseError:
                logger.exception(
                    'No se pudo registrar el uso de la clave %s', clave.pk)
            return clave.empresa_id, clave, None

    # 3. Compatibilidad: clave global de entorno.
    if _clave_global_valida(clave_presentada):
        logger.info(
            'Webhook autenticado con la clave global de entorno; '
            'se recomienda migrar a una clave por empresa'
        )
        return None, None, None

    prefijo_mostrado = clave_presentada[:LONGITUD_PREFIJO]
    logger.warning(
        'Webhook rechazado: clave invalida (prefijo %s…) desde %s',
        prefijo_mostrado, request.META.get('REMOTE_ADDR')
    )
    return None, None, 'clave invalida'


def resolver_empresa_webhook(request, empresa_solicitada=None):
    """Resuelve la empresa para un webhook entrante.

    Devuelve (empresa, error). `empresa` puede ser None cuando la peticion se
    autentico con la clave global, en cuyo caso se usa `empresa_solicitada`
    (el `empresa_id` del cuerpo), que es el comportamiento historico.

    Con una clave por empresa, la empresa de la clave SIEMPRE prevalece y se
    ignora el `empresa_id` del cuerpo.
    """
    from bases.models import Empresas

    empresa_id_clave, _clave, error = validar_clave_webhook(request)
    if error:
        return None, error

    if empresa_id_clave is not None:
        empresa = Empresas.objects.filter(id=empresa_id_clave).first()
        if not empresa:
            return None, 'la empresa de la clave ya no existe'
        return empresa, None

    # Clave global: se mantiene el comportamiento anterior.
    if empresa_solicitada is not None:
        empresa = Empresas.objects.filter(id=empresa_solicitada).first()
        if empresa:
            return empresa, None
        return None, 'No existe una empresa con id %s' % empresa_solicitada

    return None, ('Se requiere empresa_id cuando se usa la clave global '
                  'de entorno')
