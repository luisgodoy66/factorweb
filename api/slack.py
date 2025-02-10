from slack_sdk import WebClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from slack_sdk.signature import SignatureVerifier
import os

def enviar_solicitud_aprobacion(request):
    # Token de tu bot de Slack
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        return JsonResponse({"status": "Token de Slack no configurado"}, status=500)
    
    client = WebClient(token=slack_token)
    valor = 50000
    operacion = 'A00001'
    cliente = 'LUIS GODOY'

    # Enviar un mensaje a un canal o usuario
    response = client.chat_postMessage(
        channel="#todo-codigobambu",  # Ejemplo: "#general" o "@usuario"
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
                    "value": json.dumps({"action": "aprobar", "cliente": cliente, "operacion": operacion, "valor": valor})
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
                    "value": json.dumps({"action": "rechazar", "cliente": cliente, "operacion": operacion, "valor": valor})
                }
            }
        ]
    )

    return JsonResponse({"status": "Mensaje enviado", "response": response.data})

slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

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
        response_url = payload["response_url"]  # URL para enviar respuestas adicionales
        action_value = json.loads(payload["actions"][0]["value"])

        action = action_value["action"]
        cliente = action_value["cliente"]
        operacion = action_value["operacion"]
        valor = action_value["valor"]

        if action == "aprobar":
            # Lógica para aprobar la operación
            enviar_respuesta_asincrona(response_url, f"Operación aprobada por <@{user_id}>")
            return JsonResponse({"status": "Operación aprobada ✅", "cliente": cliente, "operacion": operacion, "valor": valor})
        elif action == "rechazar":
            # Lógica para rechazar la operación
            enviar_respuesta_asincrona(response_url, f"Operación rechazada por <@{user_id}>")
            return JsonResponse({"status": "Operación rechazada ❌", "cliente": cliente, "operacion": operacion, "valor": valor})
        else:
            return JsonResponse({"status": "Acción no reconocida"}, status=400)
    

import requests

def enviar_respuesta_asincrona(response_url, mensaje):
    data = {
        "text": mensaje,
        "response_type": "in_channel"  # Opcional: muestra la respuesta en el canal
    }
    requests.post(response_url, json=data)