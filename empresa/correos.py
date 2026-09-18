import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from .models import Configuracion_correos

TIPO_CORREO_CLIENTES = 'CRM'


def enviar_correo_liquidacion(empresa, destinatario, nombre_cliente
                               , codigo_asignacion, pdf_nombre, pdf_bytes):
    # notifica al cliente que su solicitud fue liquidada, adjuntando el PDF
    # de la liquidación. Devuelve (True, None) u (False, mensaje_de_error)
    if not destinatario:
        return False, "El cliente no tiene un correo electrónico registrado"

    config = Configuracion_correos.objects\
        .filter(empresa=empresa, cxtipo=TIPO_CORREO_CLIENTES, leliminado=False)\
        .first()
    if not config:
        return False, "No existe configuración de correo de clientes (CRM) para la empresa"

    asunto = config.ctasuntocorreo or "Liquidación de solicitud {0}".format(codigo_asignacion)
    cuerpo = ("Estimado(a) {0},\n\n"
              "Le informamos que su solicitud {1} ha sido liquidada.\n"
              "Adjuntamos el PDF con el detalle de la liquidación.\n\n"
              "Saludos cordiales.").format(nombre_cliente, codigo_asignacion)

    mensaje = MIMEMultipart()
    mensaje['From'] = config.ctnombreremitente or config.ctlogincorreo
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    adjunto = MIMEApplication(pdf_bytes, _subtype='pdf')
    adjunto.add_header('Content-Disposition', 'attachment', filename=pdf_nombre)
    mensaje.attach(adjunto)

    try:
        with smtplib.SMTP(config.ctservidorcorreosaliente, config.npuerto) as servidor:
            servidor.starttls()
            servidor.login(config.ctlogincorreo, config.ctpasswordcorreo)
            servidor.sendmail(config.ctlogincorreo, [destinatario], mensaje.as_string())
        return True, None
    except Exception as error:
        return False, str(error)
