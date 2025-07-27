from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from solicitudes.models import Asignacion, Niveles_aprobacion, \
    Solicitud_aprobacion, Respuesta_aprobacion
from bases.models import Usuario_empresa
from .models import Configuracion_slack

from bases.views import enviarPost
from operaciones.reportes import ImpresionLiquidacion

import json
import os

# slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

def enviar_solicitud_aprobacion(request, id_solicitud):

    # determinar el canal de aprobacion requerido
    asignacion = Asignacion.objects.get(pk=id_solicitud)

    nivel_aprobacion = Niveles_aprobacion.objects\
        .filter(nmontominimo__lte=asignacion.neto(),
                empresa=asignacion.cxcliente.empresa)\
        .order_by('nmontominimo').first()
    
    if not nivel_aprobacion:
        asignacion.lrequiereaprobacion = False
        asignacion.save()
        return HttpResponse("No se encontró nivel de aprobación para el monto mostrado. La operación no requiere aprobación"
                            , status=200)
    
    configuracion_slack = nivel_aprobacion.configuracionslack
    if not configuracion_slack:
        return HttpResponse("No se encontró canal de Slack"
                            , status=404)
    
    if configuracion_slack.lactivo == False:
        return HttpResponse("Canal de Slack no activo", status=404)
    
    if configuracion_slack.ctslackchannelname == "":
        return HttpResponse("Nombre de canal de Slack no configurado"
                            , status=404)
    
    # Token de tu bot de Slack
    slack_token = configuracion_slack.ctslackbottoken
    if not slack_token:
        return HttpResponse("Token de Slack no configurado", status=500)
    
    client = WebClient(token=slack_token)
    valor = "{:,.2f}".format(asignacion.neto())  # Convertir a cadena de texto con formato
    operacion = asignacion.cxasignacion
    cliente = asignacion.cxcliente.ctnombre

    # Enviar un mensaje a un canal o usuario
    try:
        # Crear el PDF para adjuntar
        if ImpresionLiquidacion(request,id_solicitud,True) == "OK":
            print("PDF generado correctamente")

        # usar la misma ruta para el archivo que se genera en ImpresionLiquidacion
        filepath = os.path.join(settings.MEDIA_ROOT, f"asignacion_{id_solicitud}.pdf")

        # 1. Subir el archivo. Esto crea un mensaje en el canal.
        response_file = client.files_upload_v2(
            channel=configuracion_slack.ctslackchannelname,
            file=filepath,
            title="Solicitud de factoring",
            initial_comment=f"Solicitud de aprobación para {cliente} - {operacion}"
        )
        print(response_file)
        # 2. Obtener el timestamp del mensaje del archivo para usarlo en el hilo.
        # file_message_ts = response_file['file']['shares']['public'][configuracion_slack.ctslackchannelname][0]['ts']
        file_message_ts = response_file['file']['timestamp']

        # 3. Enviar el mensaje con los botones como una respuesta en el hilo.
        response = client.chat_postMessage(
            channel=configuracion_slack.ctslackchannelname,
            thread_ts=file_message_ts,  # Esto anida el mensaje debajo del archivo.
            text=f"¿Aprobarías esta operación?\nCliente: {cliente}\nOperación: {operacion}\nValor: {valor}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"¿Aprobarías esta operación?\n*Cliente:* {cliente}\n*Operación:* {operacion}\n*Valor:* {valor}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Aprobar"
                        },
                        "style": "primary",
                        "value": json.dumps({"action": "aprobar", "operacion": asignacion.id})
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": " "
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Rechazar"
                        },
                        "style": "danger",
                        "value": json.dumps({"action": "rechazar", "operacion": asignacion.id })
                    }
                }
            ]
        )
    except FileNotFoundError:
        # print(f"❌ Error: No se encontró el archivo en la ruta '{filepath}'")
        print("❌ Error: No se encontró el archivo en la ruta ")
        return HttpResponse("Error: No se encontró el archivo PDF en la ruta "+filepath, status=404)
    except SlackApiError as e:
        # Maneja errores de la API [[1](https://translate.google.com/translate?u=https://stackoverflow.com/questions/43464873/how-to-upload-files-to-slack-using-file-upload-and-requests&hl=es&sl=en&tl=es&client=srp)]
        print(f"❌ Error al enviar el archivo a Slack: {e.response['error']}")
    # except Exception as e:
        return HttpResponse("Error al enviar mensaje al canal " 
                            + configuracion_slack.ctslackchannelname + ": " 
                            + str(e.response['error']), status=500)

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # crear registro de solicitud de aprobación
    solicitud_aprobacion = Solicitud_aprobacion.objects.create(
        asignacion=asignacion.id,
        nivel=nivel_aprobacion,
        jnotificaciones=response.data,
        cxusuariocrea = request.user,
        empresa = id_empresa.empresa,
    )
    asignacion.solicitudaprobacion = solicitud_aprobacion
    asignacion.save()

    return HttpResponse("OK", status=200)

def reenviar_solicitud_aprobacion(request, id_solicitud):

    # buscar solicitud anterior
    anterior = Solicitud_aprobacion.objects\
        .filter(asignacion=id_solicitud, cxestado = 'P').first()
    
    if not anterior:
        return HttpResponse("No se encontró solicitud de aprobación pendiente"
                            , status=404)
    
    respuesta = enviar_solicitud_aprobacion(request, id_solicitud)

    if respuesta.status_code == 200:
        anterior.cxestado = 'X'
        anterior.save()

    return respuesta

@csrf_exempt
def manejar_interactividad(request):
    if request.method == "POST":

        # Procesar la carga útil de Slack
        jsontext = request.POST.get("payload")
        payload = json.loads(jsontext)

        app_id = payload["api_app_id"]

        x = Configuracion_slack.objects\
            .filter(ctappid = app_id).first()
        
        slack_signing_secret = x.ctslacksigningsecret

        # Verificar la firma de la solicitud
        verifier = SignatureVerifier(slack_signing_secret)
        if not verifier.is_valid_request(request.body, request.headers):
            return JsonResponse({"status": f"Firma inválida {slack_signing_secret}"}, status=403)

        user_id = payload["user"]["id"]
        canal = payload["channel"]["name"]
        mensaje = payload["message"]["ts"]
        response_url = payload["response_url"]  # URL para enviar respuestas adicionales
        action_value = json.loads(payload["actions"][0]["value"])
        action = action_value["action"]
        operacion = action_value["operacion"]

        asignacion = Asignacion.objects.get(pk=operacion)
        valor = "{:,.2f}".format(asignacion.neto())  # Convertir a cadena de texto con formato
        solicitud = asignacion.cxasignacion
        cliente = asignacion.cxcliente.ctnombre

        if asignacion.solicitudaprobacion.cxestado != 'P':
            enviar_respuesta_asincrona(response_url, "Operación ya no está pendiente de aprobación")
            return HttpResponse("Operación ya no está pendiente de aprobación", status=200)
        
        # grabar el registro de la respuesta
        # nota: crear campo nombre de usuario en Respuesta_aprobacion
        sa = Solicitud_aprobacion.objects.get(pk=asignacion.solicitudaprobacion.id)
        Respuesta_aprobacion.objects.create(
            solicitud=sa,
            cxusuariorespuesta=user_id,
            cxcanal=canal,
            cxmensaje=mensaje,
            ctrespuesta=action,
            cxusuariocrea = sa.cxusuariocrea,
            empresa = sa.empresa,
        )

        if action == "aprobar":
            # Lógica para aprobar la operación
            asignacion.solicitudaprobacion.naprobaciones += 1

            if asignacion.solicitudaprobacion.naprobaciones >= asignacion.solicitudaprobacion.nivel.naprobadores:
                asignacion.solicitudaprobacion.cxestado = "A"
            
            asignacion.solicitudaprobacion.save()

            enviar_respuesta_asincrona(response_url, f"Operación de {cliente} por {valor} aprobada por <@{user_id}>")

            return JsonResponse({"status": "Operación aprobada ✅"
                                 , "cliente": asignacion.cxcliente.ctnombre
                                 , "operacion": asignacion.cxasignacion
                                 , "valor": asignacion.neto()})
        
        elif action == "rechazar":
            # Lógica para rechazar la operación
            resultado=enviarPost("CALL uspreversaliquidacionasignacion( {0},'')"
                .format( operacion,  ))
                        
            if resultado[0] == "OK"  :
                asignacion.solicitudaprobacion.cxestado = "R"
                asignacion.solicitudaprobacion.save()

                enviar_respuesta_asincrona(response_url, f"Operación de {cliente} por {valor} rechazada por <@{user_id}>")
                return JsonResponse({"status": "Operación rechazada ❌"
                                    , "cliente": asignacion.cxcliente.ctnombre
                                    , "operacion": asignacion.cxasignacion
                                    , "valor": asignacion.neto()})
            else:
                return JsonResponse({"status": "Error al intentar. {}".format(resultado)})
        else:
            return JsonResponse({"status": "Acción no reconocida"}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

    
import requests

def enviar_respuesta_asincrona(response_url, mensaje):
    data = {
        "text": mensaje,
        "response_type": "in_channel"  # Opcional: muestra la respuesta en el canal
    }
    requests.post(response_url, json=data)


    # x ={'payload': ['{"type":"block_actions"
    #                 ,"user":{"id":"U08C8QE58GG","username":"luisgodoy","name":"luisgodoy","team_id":"T08B5E6FVPH"}
    #                 ,"api_app_id":"A08C4PJLPS5"
    #                 ,"token":"99U8wg05TsuGHErXI2YsRNva"
    #                 ,"container":{"type":"message","message_ts":"1739031460.946129","channel_id":"C08BH5ASCUD","is_ephemeral":false}
    #                 ,"trigger_id":"8435169712705.8379482539799.54e1ec0c10ed8e523a3aeb86e1bb4359"
    #                 ,"team":{"id":"T08B5E6FVPH","domain":"codigobambu"},"enterprise":null,"is_enterprise_install":false
    #                 ,"channel":{"id":"C08BH5ASCUD","name":"todo-codigobambu"}
    #                 ,"message":{"user":"U08BYAP187Q"
    #                             ,"type":"message"
    #                             ,"ts":"1739031460.946129","bot_id":"B08BQDAEBD5","app_id":"A08C4PJLPS5"
    #                             ,"text":"\\u00bfAprobar\\u00edas esta operaci\\u00f3n? Cliente: LUIS GODOY Operaci\\u00f3n: A00001 Valor: 50000","team":"T08B5E6FVPH"
    #                             ,"blocks":[{"type":"section","block_id":"jJ0Hm"
    #                                         ,"text":{"type":"mrkdwn","text":"\\u00bfAprobar\\u00edas esta operaci\\u00f3n?\\nCliente: LUIS GODOY\\nOperaci\\u00f3n: A00001\\nValor: 50000","verbatim":false}
    #                                         ,"accessory":{"type":"button","style":"primary"
    #                                                       ,"text":{"type":"plain_text","text":"Aprobar","emoji":true}
    #                                                       ,"value":"{\\"action\\": \\"aprobar\\"
    #                                                                 , \\"cliente\\": \\"LUIS GODOY\\", \\"operacion\\": \\"A00001\\"
    #                                                                 , \\"valor\\": 50000}"
    #                                                       ,"action_id":"pjaiE"}}
    #                                         ,{"type":"section","block_id":"sGjwk"
    #                                         ,"text":{"type":"mrkdwn","text":" ","verbatim":false}
    #                                         ,"accessory":{"type":"button","style":"danger"
    #                                                       ,"text":{"type":"plain_text","text":"Rechazar","emoji":true}
    #                                                       ,"value":"{\\"action\\": \\"rechazar\\"
    #                                                                 , \\"cliente\\": \\"LUIS GODOY\\", \\"operacion\\": \\"A00001\\"
    #                                                                 , \\"valor\\": 50000}"
    #                                                       ,"action_id":"sg9sn"}}]}
    #                 ,"state":{"values":{}}
    #                 ,"response_url":"https:\\/\\/hooks.slack.com\\/actions\\/T08B5E6FVPH\\/8415854206726\\/p2gy08NUhrIorRVxUmWoxAid"
    #                 ,"actions":[{"action_id":"pjaiE","block_id":"jJ0Hm"
    #                              ,"text":{"type":"plain_text","text":"Aprobar","emoji":true}
    #                              ,"value":"{\\"action\\": \\"aprobar\\"
    #                                         , \\"cliente\\": \\"LUIS GODOY\\", \\"operacion\\": \\"A00001\\"
    #                                         , \\"valor\\": 50000}"
    #                              ,"style":"primary","type":"button"
    #                              ,"action_ts":"1739031829.450234"}]}']}


# {
#     'ok': True, 'files': [{'id': 'F097NPT1B0C'
#                         , 'created': 1753577295
#                         , 'timestamp': 1753577295
#                         , 'name': 'asignacion_158.pdf'
#                         , 'title': 'Solicitud de factoring'
#                         , 'mimetype': '', 'filetype': ''
#                         , 'pretty_type': '', 'user': 'U08EYNZPSSD'
#                         , 'user_team': 'T08EYNLHQQ1', 'editable': False
#                         , 'size': 12889, 'mode': 'hosted', 'is_external': False
#                         , 'external_type': '', 'is_public': False
#                         , 'public_url_shared': False, 'display_as_bot': False
#                         , 'username': ''
#                         , 'url_private': 'https://files.slack.com/files-pri/T08EYNLHQQ1-F097NPT1B0C/asignacion_158.pdf'
#                         , 'url_private_download': 'https://files.slack.com/files-pri/T08EYNLHQQ1-F097NPT1B0C/download/asignacion_158.pdf'
#                         , 'media_display_type': 'unknown'
#                         , 'permalink': 'https://factoringsede.slack.com/files/U08EYNZPSSD/F097NPT1B0C/asignacion_158.pdf'
#                         , 'permalink_public': 'https://slack-files.com/T08EYNLHQQ1-F097NPT1B0C-589c00900a'
#                         , 'comments_count': 0, 'is_starred': False
#                         , 'shares': {}, 'channels': [], 'groups': [], 'ims': []
#                         , 'has_more_shares': False, 'has_rich_preview': False
#                         , 'file_access': 'visible'}]
#     , 'file': {
#         'id': 'F097NPT1B0C', 'created': 1753577295, 'timestamp': 1753577295
#         , 'name': 'asignacion_158.pdf', 'title': 'Solicitud de factoring'
#         , 'mimetype': '', 'filetype': '', 'pretty_type': '', 'user': 'U08EYNZPSSD'
#         , 'user_team': 'T08EYNLHQQ1', 'editable': False, 'size': 12889, 'mode': 'hosted'
#         , 'is_external': False, 'external_type': '', 'is_public': False
#         , 'public_url_shared': False, 'display_as_bot': False, 'username': ''
#         , 'url_private': 'https://files.slack.com/files-pri/T08EYNLHQQ1-F097NPT1B0C/asignacion_158.pdf'
#         , 'url_private_download': 'https://files.slack.com/files-pri/T08EYNLHQQ1-F097NPT1B0C/download/asignacion_158.pdf'
#         , 'media_display_type': 'unknown'
#         , 'permalink': 'https://factoringsede.slack.com/files/U08EYNZPSSD/F097NPT1B0C/asignacion_158.pdf'
#         , 'permalink_public': 'https://slack-files.com/T08EYNLHQQ1-F097NPT1B0C-589c00900a'
#         , 'comments_count': 0, 'is_starred': False, 'shares': {}, 'channels': [], 'groups': [], 'ims': []
#         , 'has_more_shares': False, 'has_rich_preview': False, 'file_access': 'visible'}
#     }    