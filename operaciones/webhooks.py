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
    """Envia el correo de liquidacion al cliente de una o varias solicitudes.

    Cuerpo admitido:
        {"asignacion_id": 158}
        {"asignacion_ids": [158, 159]}
        {"asignacion_ids": "158,159"}
        {"asignacion_id": 158, "forzar": true}

    Responde con el detalle por solicitud para que n8n pueda ramificar y
    registrar. Es idempotente por defecto: reenviar no duplica el correo salvo
    que se pida `forzar`.
    """
    from .servicios import enviar_liquidacion

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

    ids = _normalizar_ids(datos.get('asignacion_ids')
                          if datos.get('asignacion_ids') is not None
                          else datos.get('asignacion_id'))
    if not ids:
        return JsonResponse(
            {'ok': False,
             'error': 'Se requiere asignacion_id o asignacion_ids'},
            status=400)

    forzar = str(datos.get('forzar', '')).strip().lower() in (
        '1', 'true', 'yes', 'si', 'sí', 'on')

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
        'solicitados': len(ids),
        'enviados': enviados,
        'ya_enviadas': ya_enviadas,
        'fallidos': fallidos,
        'resultados': resultados,
    }, status=200 if fallidos == 0 else 207)
