"""Webhooks entrantes de operaciones, invocados por automatizaciones (n8n).

Autenticacion: cabecera X-Margarita-Key (o X-Margarita-API-Key) con una clave
de empresa de empresa.Claves_webhook. La empresa se determina por la clave, no
por el cuerpo de la peticion.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from empresa.claves import resolver_empresa_webhook

logger = logging.getLogger(__name__)


def _leer_cuerpo(request):
    """Devuelve el cuerpo de la peticion como dict, admitiendo JSON o form."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            datos = json.loads(request.body.decode('utf-8')) if request.body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None, 'Body inválido, se espera JSON'
    else:
        datos = request.POST.dict()
    if not isinstance(datos, dict):
        return None, 'El cuerpo debe ser un objeto'
    return datos, None


def _a_booleano(valor):
    return str(valor).strip().lower() in ('1', 'true', 'yes', 'si', 'sí', 'on')


def _a_entero(valor, por_defecto, minimo=None, maximo=None):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        numero = por_defecto
    if minimo is not None:
        numero = max(minimo, numero)
    if maximo is not None:
        numero = min(maximo, numero)
    return numero


def _normalizar_ids(valor):
    """Admite un id suelto, una cadena separada por comas o una lista."""
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        crudos = list(valor)
    else:
        crudos = str(valor).replace(';', ',').split(',')
    ids = []
    for c in crudos:
        c = str(c).strip()
        if not c:
            continue
        try:
            ids.append(int(c))
        except (TypeError, ValueError):
            continue
    return ids


@csrf_exempt
@require_POST
def webhook_enviar_correo_liquidacion(request):
    """Envia al cliente el correo de liquidacion, con el PDF adjunto.

    Modo puntual (una o varias solicitudes concretas):
        {"asignacion_id": 158}
        {"asignacion_ids": [158, 159]}
        {"asignacion_ids": "158,159"}
        {"asignacion_id": 158, "forzar": true}

    Modo lote: la empresa decide que notificar, sin que la automatizacion tenga
    que consultar la base de datos.
        {"lote": true, "limite": 50}
        {"lote": true, "desde": "2026-09-01", "hasta": "2026-09-30"}

    Es idempotente por defecto: reenviar no duplica el correo salvo que se pida
    `forzar`. Devuelve el detalle por solicitud para que n8n pueda ramificar.
    """
    from .servicios import enviar_liquidacion, solicitudes_pendientes_de_notificar

    datos, error = _leer_cuerpo(request)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    empresa, error_empresa = resolver_empresa_webhook(
        request, datos.get('empresa_id'))
    if error_empresa:
        logger.warning(
            'Webhook de correo de liquidacion rechazado desde %s: %s',
            request.META.get('REMOTE_ADDR'), error_empresa)
        return JsonResponse(
            {'ok': False, 'error': 'No autorizado: %s' % error_empresa},
            status=403)
    if empresa is None:
        return JsonResponse(
            {'ok': False,
             'error': 'La clave usada no identifica una empresa'},
            status=403)

    forzar = _a_booleano(datos.get('forzar'))
    modo_lote = _a_booleano(datos.get('lote'))

    if modo_lote:
        ids = solicitudes_pendientes_de_notificar(
            empresa,
            limite=_a_entero(datos.get('limite'), 50, minimo=1, maximo=500),
            desde=datos.get('desde'),
            hasta=datos.get('hasta'),
        )
        if not ids:
            return JsonResponse({
                'ok': True,
                'empresa': empresa.ctnombre,
                'modo': 'lote',
                'solicitados': 0,
                'enviados': 0,
                'ya_enviadas': 0,
                'fallidos': 0,
                'resultados': [],
                'mensaje': 'No hay solicitudes pendientes de notificar',
            })
    else:
        ids = _normalizar_ids(datos.get('asignacion_ids')
                              if datos.get('asignacion_ids') is not None
                              else datos.get('asignacion_id'))
        if not ids:
            return JsonResponse(
                {'ok': False,
                 'error': ('Se requiere asignacion_id, asignacion_ids o '
                           'lote=true')},
                status=400)

    resultados = []
    for asignacion_id in ids:
        try:
            resultados.append(
                enviar_liquidacion(asignacion_id, empresa, forzar=forzar))
        except Exception as error_envio:  # noqa: BLE001
            logger.exception(
                'Error inesperado enviando liquidacion %s', asignacion_id)
            resultados.append({
                'ok': False,
                'asignacion_id': asignacion_id,
                'cxasignacion': None,
                'destinatario': None,
                'pdf': None,
                'ya_enviada': False,
                'error': str(error_envio),
            })

    enviados = sum(1 for r in resultados if r['ok'] and not r['ya_enviada'])
    ya_enviadas = sum(1 for r in resultados if r['ya_enviada'])
    fallidos = sum(1 for r in resultados if not r['ok'])

    return JsonResponse({
        'ok': fallidos == 0,
        'empresa': empresa.ctnombre,
        'modo': 'lote' if modo_lote else 'puntual',
        'solicitados': len(ids),
        'enviados': enviados,
        'ya_enviadas': ya_enviadas,
        'fallidos': fallidos,
        'resultados': resultados,
    }, status=200 if fallidos == 0 else 207)
