"""Servicios de operaciones que pueden invocarse desde vistas o desde
automatizaciones externas (n8n) sin depender de una sesion de usuario.

El envio del correo de liquidacion vivia dentro de una vista que leia
`request.usuario_empresa`, de modo que solo podia dispararse con un clic de un
usuario autenticado. Aqui se extrae la logica a una funcion que recibe la
empresa de forma explicita.
"""
import logging

from django.db import DatabaseError
from django.utils import timezone

from solicitudes.models import Asignacion as AsignacionSolicitud
from empresa.correos import enviar_correo_liquidacion

logger = logging.getLogger(__name__)

# Estados de la solicitud para los que tiene sentido notificar la liquidacion.
ESTADOS_NOTIFICABLES = ('L', 'A')


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


def enviar_liquidacion(asignacion_id, empresa, forzar=False):
    """Envia al cliente el PDF de liquidacion de una solicitud.

    Devuelve un dict con el resultado, pensado para serializarse como JSON:
        {ok, asignacion_id, cxasignacion, destinatario, pdf, ya_enviada, error}

    Es idempotente: si la solicitud ya fue notificada y `forzar` es False, no
    vuelve a enviar. Solo se marca como notificada cuando el envio fue exitoso,
    de modo que un fallo de SMTP permite reintentar.
    """
    resultado = {
        'ok': False,
        'asignacion_id': asignacion_id,
        'cxasignacion': None,
        'destinatario': None,
        'pdf': None,
        'ya_enviada': False,
        'error': None,
    }

    # --- 1. La asignacion debe existir y pertenecer a la empresa de la clave.
    # El filtro por empresa es lo que impide que una empresa notifique
    # operaciones de otra.
    asignacion = AsignacionSolicitud.objects\
        .filter(id=asignacion_id, empresa=empresa, leliminado=False)\
        .select_related('cxcliente')\
        .first()
    if not asignacion:
        resultado['error'] = ('No existe la solicitud %s para esta empresa'
                              % asignacion_id)
        return resultado

    resultado['cxasignacion'] = asignacion.cxasignacion

    # --- 2. Idempotencia.
    if asignacion.lliquidacionnotificada and not forzar:
        resultado['ok'] = True
        resultado['ya_enviada'] = True
        resultado['destinatario'] = (asignacion.cliente.cxcliente.ctemail
                                     if asignacion.cliente else None)
        return resultado

    # --- 3. Estado: no notificar una liquidacion que no ocurrio.
    if asignacion.cxestado not in ESTADOS_NOTIFICABLES:
        resultado['error'] = (
            'La solicitud %s esta en estado %s; solo se notifica en %s'
            % (asignacion.cxasignacion, asignacion.cxestado,
               '/'.join(ESTADOS_NOTIFICABLES)))
        return resultado

    # 20-sep-26 l.g.    tomar el cliente directamente desde asignacion.cliente no al solicitante
    # cliente = asignacion.cxcliente
    cliente = asignacion.cliente
    if not cliente:
        resultado['error'] = 'La solicitud no tiene cliente asociado'
        return resultado

    destinatario = cliente.cxcliente.ctemail or asignacion.cxcliente.ctemail or cliente.cxcliente.ctemail2
    if not destinatario:
        resultado['error'] = ('El cliente %s no tiene correo electronico '
                              'registrado' % cliente.cxcliente.ctnombre)
        return resultado
    resultado['destinatario'] = destinatario

    # --- 4. PDF. Se genera sin sesion, a partir de la empresa.
    from .reportes import generar_pdf_liquidacion_para_empresa

    nombre_pdf, pdf_bytes, error_pdf = generar_pdf_liquidacion_para_empresa(
        asignacion.id, empresa)
    if error_pdf:
        resultado['error'] = 'No se pudo generar el PDF: %s' % error_pdf
        return resultado
    resultado['pdf'] = nombre_pdf

    # --- 5. Envio.
    ok, error_envio = enviar_correo_liquidacion(
        empresa,
        destinatario,
        cliente.cxcliente.ctnombre or asignacion.cxcliente.ctnombre,
        asignacion.cxasignacion,
        nombre_pdf,
        pdf_bytes,
    )
    if not ok:
        resultado['error'] = error_envio
        return resultado

    # --- 6. Marca de idempotencia. Un fallo al guardar no debe hacer creer
    # que el correo no salio: el envio ya ocurrio.
    try:
        asignacion.lliquidacionnotificada = True
        asignacion.dliquidacionnotificada = timezone.now()
        asignacion.save(update_fields=['lliquidacionnotificada',
                                       'dliquidacionnotificada'])
    except DatabaseError:
        logger.exception(
            'Se envio el correo de liquidacion %s pero no se pudo marcar '
            'como notificada', asignacion.cxasignacion)

    resultado['ok'] = True
    return resultado
