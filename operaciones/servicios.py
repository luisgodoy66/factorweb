"""Servicios de operaciones que pueden invocarse desde vistas o desde
automatizaciones externas (n8n) sin depender de una sesion de usuario.

Dos formas de notificar la liquidacion al cliente:

  1. **Envio directo por SMTP** (`enviar_liquidacion`): Django compone y envia.
     Es el camino que usa el boton de la interfaz.
  2. **Composicion para que otro envie** (`construir_correo_liquidacion` +
     `marcar_liquidacion_notificada`): Django compone el correo y entrega el PDF
     en base64; la automatizacion lo envia con su propio proveedor (por ejemplo
     el nodo nativo de Gmail de n8n) y despues confirma el envio.

Esto ultimo resuelve el caso de Gmail, cuyo SMTP exige contrasena de aplicacion
y rechaza el login con `534 5.7.9 Application-specific password required`.
"""
import base64
import logging

from django.db import DatabaseError
from django.utils import timezone

from solicitudes.models import Asignacion as AsignacionSolicitud

logger = logging.getLogger(__name__)

# Estados de la solicitud para los que tiene sentido notificar la liquidacion.
ESTADOS_NOTIFICABLES = ('L', 'A')

ASUNTO_POR_DEFECTO = 'Liquidación de solicitud {codigo}'

CUERPO_POR_DEFECTO = (
    "Estimado(a) {nombre},\n\n"
    "Le informamos que su solicitud {codigo} ha sido liquidada.\n"
    "Adjuntamos el PDF con el detalle de la liquidación.\n\n"
    "Saludos cordiales."
)


def solicitudes_pendientes_de_notificar(empresa, limite=50, desde=None,
                                        hasta=None):
    """Ids de solicitudes liquidables que aun no fueron notificadas al cliente.

    Permite que la automatizacion pida "lo pendiente de esta empresa" sin tener
    que consultar la base de datos. Ordena de la mas antigua a la mas reciente,
    de modo que un limite bajo vaya vaciando el atraso en lugar de dejar las
    mas viejas postergadas indefinidamente.

    `desde` y `hasta` filtran por la fecha de desembolso (formato AAAA-MM-DD).
    """
    consulta = AsignacionSolicitud.objects.filter(
        empresa=empresa,
        leliminado=False,
        cxestado__in=ESTADOS_NOTIFICABLES,
        lliquidacionnotificada=False,
    )

    if desde:
        consulta = consulta.filter(ddesembolso__gte=desde)
    if hasta:
        consulta = consulta.filter(ddesembolso__lte=hasta)

    return list(
        consulta.order_by('ddesembolso', 'id').values_list('id', flat=True)[:limite]
    )


def _plantilla_correo(empresa, codigo, nombre):
    """Asunto y cuerpo, tomando la configuracion CRM de la empresa si existe.

    La configuracion de correo se usa solo como plantilla de textos: para el
    envio desde n8n no hace falta que la empresa tenga SMTP configurado.
    """
    from empresa.models import Configuracion_correos

    config = Configuracion_correos.objects.filter(
        empresa=empresa, cxtipo='CRM', leliminado=False).first()

    asunto = (config.ctasuntocorreo if config and config.ctasuntocorreo
              else ASUNTO_POR_DEFECTO).format(codigo=codigo)
    cuerpo = CUERPO_POR_DEFECTO.format(nombre=nombre, codigo=codigo)
    return asunto, cuerpo


def construir_correo_liquidacion(asignacion_id, empresa, forzar=False):
    """Compone el correo de liquidacion SIN enviarlo.

    Devuelve un dict serializable:
        {ok, asignacion_id, cxasignacion, destinatario, destinatario_nombre,
         asunto, cuerpo, pdf_nombre, pdf_base64, ya_enviada, error}

    No marca nada en la base: eso lo hace `marcar_liquidacion_notificada`
    cuando la automatizacion confirma que el envio ocurrio.
    """
    resultado = {
        'ok': False,
        'asignacion_id': asignacion_id,
        'cxasignacion': None,
        'destinatario': None,
        'destinatario_nombre': None,
        'asunto': None,
        'cuerpo': None,
        'pdf_nombre': None,
        'pdf_base64': None,
        'ya_enviada': False,
        'error': None,
    }

    # La asignacion debe existir y pertenecer a la empresa de la clave. Este
    # filtro es lo que impide que una empresa notifique operaciones de otra.
    asignacion = AsignacionSolicitud.objects\
        .filter(id=asignacion_id, empresa=empresa, leliminado=False)\
        .select_related('cxcliente', 'cliente')\
        .first()
    if not asignacion:
        resultado['error'] = ('No existe la solicitud %s para esta empresa'
                              % asignacion_id)
        return resultado

    resultado['cxasignacion'] = asignacion.cxasignacion

    if asignacion.lliquidacionnotificada and not forzar:
        resultado['ok'] = True
        resultado['ya_enviada'] = True
        return resultado

    # No notificar una liquidacion que no ocurrio.
    if asignacion.cxestado not in ESTADOS_NOTIFICABLES:
        resultado['error'] = (
            'La solicitud %s esta en estado %s; solo se notifica en %s'
            % (asignacion.cxasignacion, asignacion.cxestado,
               '/'.join(ESTADOS_NOTIFICABLES)))
        return resultado

    # El cliente del contrato manda; el solicitante es el respaldo.
    cliente = asignacion.cliente
    if not cliente:
        resultado['error'] = 'La solicitud no tiene cliente asociado'
        return resultado

    solicitante = asignacion.cxcliente
    # Orden de preferencia: los datos del cliente del contrato primero (es la
    # contraparte legal), y solo despues el solicitante. El alterno del cliente
    # va antes que el principal del solicitante: si el cliente registro un
    # segundo correo, es mas fiable que el del solicitante.
    destinatario = (
        cliente.cxcliente.ctemail
        or cliente.cxcliente.ctemail2
        or (solicitante.ctemail if solicitante else None)
        or (solicitante.ctemail2 if solicitante else None)
    )
    if not destinatario:
        resultado['error'] = ('El cliente %s no tiene correo electronico '
                              'registrado' % cliente.cxcliente.ctnombre)
        return resultado

    nombre_cliente = (cliente.cxcliente.ctnombre
                      or (solicitante.ctnombre if solicitante else '')) or ''
    asunto, cuerpo = _plantilla_correo(empresa, asignacion.cxasignacion,
                                       nombre_cliente)

    # PDF: se genera sin sesion, a partir de la empresa.
    from .reportes import generar_pdf_liquidacion_para_empresa

    nombre_pdf, pdf_bytes, error_pdf = generar_pdf_liquidacion_para_empresa(
        asignacion.id, empresa)
    if error_pdf:
        resultado['error'] = 'No se pudo generar el PDF: %s' % error_pdf
        return resultado

    resultado.update({
        'ok': True,
        'destinatario': destinatario,
        'destinatario_nombre': nombre_cliente,
        'asunto': asunto,
        'cuerpo': cuerpo,
        'pdf_nombre': nombre_pdf,
        'pdf_base64': base64.b64encode(pdf_bytes).decode('ascii'),
    })
    return resultado


def marcar_liquidacion_notificada(asignacion_id, empresa, forzar=True):
    """Marca una solicitud como notificada, tras confirmar el envio externo.

    Devuelve {ok, asignacion_id, cxasignacion, ya_estaba, error}. No comprueba
    el estado de la solicitud: quien llama ya construyo el correo con exito.
    """
    asignacion = AsignacionSolicitud.objects.filter(
        id=asignacion_id, empresa=empresa, leliminado=False).first()
    if not asignacion:
        return {'ok': False, 'asignacion_id': asignacion_id,
                'cxasignacion': None, 'ya_estaba': False,
                'error': 'No existe la solicitud %s para esta empresa'
                         % asignacion_id}

    ya_estaba = asignacion.lliquidacionnotificada
    if not ya_estaba or forzar:
        try:
            asignacion.lliquidacionnotificada = True
            asignacion.dliquidacionnotificada = timezone.now()
            asignacion.save(update_fields=['lliquidacionnotificada',
                                           'dliquidacionnotificada'])
        except DatabaseError as error:
            logger.exception(
                'No se pudo marcar como notificada la solicitud %s',
                asignacion.cxasignacion)
            return {'ok': False, 'asignacion_id': asignacion_id,
                    'cxasignacion': asignacion.cxasignacion,
                    'ya_estaba': ya_estaba, 'error': str(error)}

    return {'ok': True, 'asignacion_id': asignacion_id,
            'cxasignacion': asignacion.cxasignacion,
            'ya_estaba': ya_estaba, 'error': None}


def enviar_liquidacion(asignacion_id, empresa, user=None, forzar=False):
    """Compone y envia la liquidacion por SMTP, y la marca como notificada.

    Devuelve el mismo dict que `construir_correo_liquidacion` mas el resultado
    del envio: {ok, ..., ya_enviada, error}.

    Es idempotente: si la solicitud ya fue notificada y `forzar` es False, no
    vuelve a enviar. Solo se marca como notificada cuando el envio fue exitoso,
    de modo que un fallo permite reintentar.
    """
    from empresa.correos import enviar_correo_liquidacion

    composicion = construir_correo_liquidacion(asignacion_id, empresa, forzar)
    if not composicion['ok'] or composicion['ya_enviada']:
        # Se descarta el PDF: no hace falta para la respuesta.
        composicion.pop('pdf_base64', None)
        return composicion

    pdf_bytes = base64.b64decode(composicion['pdf_base64'])
    ok, error_envio = enviar_correo_liquidacion(
        empresa,
        composicion['destinatario'],
        composicion['destinatario_nombre'],
        composicion['cxasignacion'],
        composicion['pdf_nombre'],
        pdf_bytes,
    )
    if not ok:
        composicion.pop('pdf_base64', None)
        composicion['ok'] = False
        composicion['error'] = error_envio
        return composicion

    marcar_liquidacion_notificada(asignacion_id, empresa, forzar=True)

    composicion.pop('pdf_base64', None)
    composicion['ok'] = True
    return composicion
