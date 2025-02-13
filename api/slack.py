from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from solicitudes.models import Asignacion, Niveles_aprobacion, \
    Solicitud_aprobacion, Respuesta_aprobacion
from bases.models import Usuario_empresa

from bases.views import enviarPost
import json
import os

slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

def enviar_solicitud_aprobacion(request, id_solicitud):

    # determinar el canal de aprobacion requerido
    asignacion = Asignacion.objects.get(pk=id_solicitud)

    nivel_aprobacion = Niveles_aprobacion.objects\
        .filter(nmontominimo__lte=asignacion.neto())\
        .order_by('nmontominimo').first()
    
    if not nivel_aprobacion:
        asignacion.lrequiereaprobacion = False
        asignacion.save()
        return HttpResponse("No se encontró nivel de aprobación"
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
        
        response = client.chat_postMessage(
            channel=configuracion_slack.ctslackchannelname,
            text=f"¿Aprobarías esta operación?\nCliente: {cliente}\nOperación: {operacion}\nValor: {valor}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"¿Aprobarías esta operación?\nCliente: {cliente}\nOperación: {operacion}\nValor: {valor}"
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
    except Exception as e:
        return HttpResponse("Error al enviar mensaje"+ str(e), status=500)
    
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
    # Verificar la firma de la solicitud
        verifier = SignatureVerifier(slack_signing_secret)
        if not verifier.is_valid_request(request.body, request.headers):
            return JsonResponse({"status": f"Firma inválida {slack_signing_secret}"}, status=403)

        # Procesar la carga útil de Slack
        jsontext = request.POST.get("payload")
        payload = json.loads(jsontext)
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
        id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
        sa = Solicitud_aprobacion.objects.get(pk=asignacion.solicitudaprobacion.id)
        Respuesta_aprobacion.objects.create(
            solicitud=sa,
            cxusuariorespuesta=user_id,
            # cxcanal=canal,
            # cxmensaje=mensaje,
            # ctrespuesta=action,
            cxusuariocrea = request.user,
            empresa = id_empresa.empresa,
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
        
        # nota: grabar en la base de datos el resultado de la aprobación

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
    
import requests

def enviar_respuesta_asincrona(response_url, mensaje):
    data = {
        "text": mensaje,
        "response_type": "in_channel"  # Opcional: muestra la respuesta en el canal
    }
    requests.post(response_url, json=data)


    # x ={'payload': ['{"type":"block_actions"
    #                 ,"user":{"id":"U08C8QE58GG","username":"luisgodoy","name":"luisgodoy","team_id":"T08B5E6FVPH"}
    #                 ,"api_app_id":"A08C4PJLPS5","token":"99U8wg05TsuGHErXI2YsRNva"
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