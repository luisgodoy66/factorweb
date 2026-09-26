"""Webhooks entrantes de operaciones, invocados por automatizaciones (n8n).

Autenticacion: cabecera X-Margarita-Key (o X-Margarita-API-Key) con una clave
de empresa de empresa.Claves_webhook. La empresa se determina por la clave, no
por el cuerpo de la peticion.

Dos formas de notificar la liquidacion:

  * **Django envia por SMTP** — modos `puntual` y `lote`.
  * **n8n envia con su propio proveedor** — `webhook_datos_correo_liquidacion`
    compone el correo y entrega el PDF en base64; el flujo lo envia con el nodo
    nativo de Gmail y despues llama a `webhook_confirmar_correo_liquidacion`.
    Esta via evita el SMTP de Gmail, que exige contrasena de aplicacion.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from empresa.claves import resolver_empresa_webhook

logger = logging.getLogger(__name__)


def _datos_peticion(request):
    """Datos de la peticion, admitiendo JSON, formulario o querystring.

    Las llamadas por item del flujo de n8n son GET con parametros en la URL, de
    modo que un id suelto no obliga a construir un cuerpo.
    """
    if request.content_type and 'application/json' in request.content_type:
        try:
            datos = json.loads(request.body.decode('utf-8')) if request.body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None, 'Body inválido, se espera JSON'
        if not isinstance(datos, dict):
            return None, 'El cuerpo debe ser un objeto'
        return datos, None

    if request.POST:
        return request.POST.dict(), None
    return request.GET.dict(), None


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


def _resolver_empresa(request, datos):
    """Devuelve (empresa, respuesta_de_error)."""
    empresa, error = resolver_empresa_webhook(request, datos.get('empresa_id'))
    if error:
        logger.warning(
            'Webhook de liquidacion rechazado desde %s: %s',
            request.META.get('REMOTE_ADDR'), error)
        return None, JsonResponse(
            {'ok': False, 'error': 'No autorizado: %s' % error}, status=403)
    if empresa is None:
        return None, JsonResponse(
            {'ok': False, 'error': 'La clave usada no identifica una empresa'},
            status=403)
    return empresa, None


@csrf_exempt
@require_POST
def webhook_enviar_correo_liquidacion(request):
    """Envia el correo de liquidacion desde Django, por SMTP.

    Modo puntual:
        {"asignacion_id": 158}
        {"asignacion_ids": [158, 159]}
        {"asignacion_ids": "158,159"}
        {"asignacion_id": 158, "forzar": true}

    Modo lote (la empresa decide que notificar):
        {"lote": true, "limite": 50}
        {"lote": true, "desde": "2026-09-01", "hasta": "2026-09-30"}

    Idempotente por defecto. Devuelve 200 si todo fue bien y 207 si algo fallo.
    """
    from .servicios import enviar_liquidacion, solicitudes_pendientes_de_notificar

    datos, error = _datos_peticion(request)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    empresa, respuesta_error = _resolver_empresa(request, datos)
    if respuesta_error:
        return respuesta_error

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
                'ok': True, 'empresa': empresa.ctnombre, 'modo': 'lote',
                'solicitados': 0, 'enviados': 0, 'ya_enviadas': 0,
                'fallidos': 0, 'resultados': [],
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
                'ok': False, 'asignacion_id': asignacion_id,
                'cxasignacion': None, 'destinatario': None, 'pdf': None,
                'ya_enviada': False, 'error': str(error_envio),
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


@csrf_exempt
def webhook_datos_correo_liquidacion(request):
    """Compone el correo de liquidacion y lo entrega para que otro lo envie.

    No envia nada ni marca la solicitud. Acepta GET y POST.

        GET  ...?asignacion_id=158            -> un correo, con su PDF
        GET  ...?lote=true&limite=50          -> ids de las pendientes
        POST {"asignacion_ids": [158,159]}    -> esos ids

    Cada item de la respuesta:
        {ok, asignacion_id, cxasignacion, destinatario, asunto, cuerpo,
         pdf_nombre, pdf_base64}
    """
    from .servicios import (construir_correo_liquidacion,
                            solicitudes_pendientes_de_notificar)

    datos, error = _datos_peticion(request)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    empresa, respuesta_error = _resolver_empresa(request, datos)
    if respuesta_error:
        return respuesta_error

    forzar = _a_booleano(datos.get('forzar'))
    con_pdf = datos.get('con_pdf')
    con_pdf = True if con_pdf is None else _a_booleano(con_pdf)

    ids = _normalizar_ids(datos.get('asignacion_ids')
                          if datos.get('asignacion_ids') is not None
                          else datos.get('asignacion_id'))
    modo = 'puntual'
    if not ids:
        if not _a_booleano(datos.get('lote')):
            return JsonResponse(
                {'ok': False,
                 'error': ('Se requiere asignacion_id, asignacion_ids o '
                           'lote=true')},
                status=400)
        modo = 'lote'
        ids = solicitudes_pendientes_de_notificar(
            empresa,
            limite=_a_entero(datos.get('limite'), 50, minimo=1, maximo=500),
            desde=datos.get('desde'),
            hasta=datos.get('hasta'),
        )

    correos = []
    for asignacion_id in ids:
        try:
            correo = construir_correo_liquidacion(asignacion_id, empresa,
                                                  forzar)
        except Exception as error_comp:  # noqa: BLE001
            logger.exception(
                'Error inesperado componiendo la liquidacion %s', asignacion_id)
            correo = {'ok': False, 'asignacion_id': asignacion_id,
                      'error': str(error_comp)}
        if not con_pdf:
            correo.pop('pdf_base64', None)
        correos.append(correo)

    listos = sum(1 for c in correos if c.get('ok') and not c.get('ya_enviada'))
    ya = sum(1 for c in correos if c.get('ya_enviada'))
    fallidos = sum(1 for c in correos if not c.get('ok'))

    return JsonResponse({
        'ok': fallidos == 0,
        'empresa': empresa.ctnombre,
        'modo': modo,
        'solicitados': len(ids),
        'listos': listos,
        'ya_enviadas': ya,
        'fallidos': fallidos,
        'correos': correos,
    }, status=200 if fallidos == 0 else 207)


@csrf_exempt
@require_POST
def webhook_confirmar_correo_liquidacion(request):
    """Confirma que los correos fueron enviados y marca las solicitudes.

    Lo llama el flujo despues de enviar, para que la marca de idempotencia quede
    registrada por Django y no se repita el envio en la corrida siguiente.

        {"asignacion_ids": [158, 159]}
        {"asignacion_id": 158}
    """
    from .servicios import marcar_liquidacion_notificada

    datos, error = _datos_peticion(request)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    empresa, respuesta_error = _resolver_empresa(request, datos)
    if respuesta_error:
        return respuesta_error

    ids = _normalizar_ids(datos.get('asignacion_ids')
                          if datos.get('asignacion_ids') is not None
                          else datos.get('asignacion_id'))
    if not ids:
        return JsonResponse(
            {'ok': False, 'error': 'Se requiere asignacion_id o asignacion_ids'},
            status=400)

    forzar = _a_booleano(datos.get('forzar'))
    marcas = [marcar_liquidacion_notificada(i, empresa, forzar=forzar)
              for i in ids]
    fallidos = sum(1 for m in marcas if not m['ok'])

    return JsonResponse({
        'ok': fallidos == 0,
        'empresa': empresa.ctnombre,
        'confirmadas': len(marcas) - fallidos,
        'fallidos': fallidos,
        'resultados': marcas,
    }, status=200 if fallidos == 0 else 207)
