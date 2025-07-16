# # import os
# # from sendgrid import SendGridAPIClient
# # from sendgrid.helpers.mail import *
# # ... (código de sendgrid comentado) ...
# #     print(response.status_code)
# #     print(response.body)
# #     print(response.headers)

from django.http import HttpResponse, JsonResponse
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt

from api.models import Configuracion_twilio_whatsapp
from cobranzas.models import Gestion_cobro, Twilio_whatsapp
from bases.models import Usuario_empresa
import json

def enviar_mensaje_whatsapp(request, whatsapp_destino ):
    datos = json.loads(request.body.decode('utf-8'))  # Imprime el cuerpo de la solicitud para depuración
    if request.method == 'POST':
        # Lees los parámetros enviados en el cuerpo de la solicitud POST
        cuerpo_mensaje = datos.get('cuerpo_mensaje')
        gestion_cobro_id = datos.get('gestion_cobro_id')

        if not cuerpo_mensaje or not gestion_cobro_id:
            return JsonResponse({'status': 'error', 'message': 'Faltan parámetros.'}, status=400)
        id_empresa = Usuario_empresa.objects\
            .filter(user = request.user).first()

        configuracion_twilio = Configuracion_twilio_whatsapp.objects\
            .filter(empresa=id_empresa.empresa, lactivo=True).first()
                
        if not configuracion_twilio:
            return HttpResponse("Configuración de Twilio no encontrada.")
        
        gestion_cobro = Gestion_cobro.objects.get(id=gestion_cobro_id)
        if not gestion_cobro:
            raise HttpResponse("Gestión de cobro no encontrada.")

        try:

            account_sid = configuracion_twilio.ctaccountsid
            auth_token = configuracion_twilio.ctauthtoken
            whatsapp_origen = 'whatsapp:' + configuracion_twilio.ctwhatsappnumber

            client = Client(account_sid, auth_token)

            print(f"Enviando mensaje a {whatsapp_destino} desde {whatsapp_origen}")
            message = client.messages.create(
                from_=whatsapp_origen,
                body=cuerpo_mensaje,
                to='whatsapp:' + whatsapp_destino  # Reemplaza con el número de destino
            )

            # Guarda el mensaje enviado en la base de datos
            mensaje_enviado = Twilio_whatsapp(
                ctsid=message.sid,
                ctbody=cuerpo_mensaje,
                ctto='whatsapp:' + whatsapp_destino,  # Reemplaza con el número de destino
                gestion_cobro=gestion_cobro,
                configuracion=configuracion_twilio,
                ctfrom=whatsapp_origen,
                ctstatus=message.status,
                jcontexto=json.dumps(datos),  # Guarda el contexto de la solicitud
                cxusuariocrea=request.user,
                empresa=id_empresa.empresa
            )
            mensaje_enviado.save()

            if gestion_cobro.cxestado == 'P':
                gestion_cobro.cxestado = 'A'
                gestion_cobro.save()

            return HttpResponse("OK")
            
        except Exception as e:
            return HttpResponse( str(e), status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

def historial_mensajes_whatsapp(request, gestion_cobro_id):
    # Obtiene la gestión de cobro
    gestion_cobro = Gestion_cobro.objects.get(id=gestion_cobro_id)
    
    # Filtra los mensajes enviados para esa gestión de cobro
    mensajes = Twilio_whatsapp.objects\
      .filter(gestion_cobro=gestion_cobro)\
      .order_by('dregistro')  # Ordena por fecha de creación ascendente

    mensajes_list = list(mensajes.values())
    response_data = {
        'cantidad': len(mensajes_list),
        'mensajes': mensajes_list
    }
    return JsonResponse(response_data, safe=False)

@csrf_exempt
def webhook_whatsapp_twilio(request):
    """
    Endpoint para recibir mensajes entrantes de WhatsApp desde Twilio.
    Guarda los datos relevantes en la tabla Twilio_whatsapp.
    """
    if request.method == 'POST':
        # Twilio envía los datos como application/x-www-form-urlencoded
        from_number = request.POST.get('From', '')
        to_number = request.POST.get('To', '')
        body = request.POST.get('Body', '')
        sid = request.POST.get('MessageSid', '')
        status = request.POST.get('SmsStatus', '')
        direction = request.POST.get('Direction', '')
        # Puedes agregar más campos según lo que Twilio envíe

        # Busca la configuración activa de Twilio
        configuracion = Configuracion_twilio_whatsapp.objects\
          .filter(lactivo=True).first()
        
        if not configuracion:
            return JsonResponse({'error': 'Configuración de Twilio no encontrada'}, status=404)

        # Busca la gestión de cobro asociada al número del cliente (si aplica)
        numero_whatsapp = from_number.replace('whatsapp:', '')
        gestion_cobro = Gestion_cobro.objects\
          .filter(ctnumerowhatsapp=numero_whatsapp, cxestado='A').first()

        if not gestion_cobro:
            # nota: cambiar a la validación correcta
            gestion_cobro = Gestion_cobro.objects\
              .filter(empresa=configuracion.empresa).first()

        # Guarda el mensaje en la tabla
        Twilio_whatsapp.objects.create(
            configuracion=configuracion,
            gestion_cobro=gestion_cobro,
            ctfrom=from_number,
            ctto=to_number,
            ctbody=body,
            ctsid=sid,
            ctstatus=status,
            ctdirection=direction,
            jcontexto=json.dumps(dict(request.POST),),
            cxusuariocrea=configuracion.cxusuariocrea,  # No hay usuario asociado en este caso
            empresa=configuracion.empresa if configuracion else None
        )

        return HttpResponse("OK", status=200)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

