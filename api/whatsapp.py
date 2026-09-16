# views.py
import hmac
import hashlib
import logging
import os

import requests
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def _firma_meta_valida(request):
    """Valida la cabecera X-Hub-Signature-256 que envia Meta.

    Meta firma el cuerpo CRUDO del request con el App Secret (HMAC-SHA256).
    Sin esta validacion el webhook es publico y cualquiera puede inyectar
    eventos falsos de WhatsApp.

    Devuelve (es_valida, motivo).
    """
    app_secret = getattr(settings, 'WHATSAPP_APP_SECRET', None)
    if not app_secret:
        return False, 'WHATSAPP_APP_SECRET no configurado'

    firma = request.headers.get('X-Hub-Signature-256', '')
    if not firma.startswith('sha256='):
        return False, 'falta la cabecera X-Hub-Signature-256'

    partes = firma.split('=', 1)
    if len(partes) != 2:
        return False, 'formato de firma invalido'

    esperada = hmac.new(
        app_secret.encode('utf-8'),
        request.body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(esperada, partes[1]):
        return False, 'firma invalida'
    return True, 'ok'

def enviar_mensaje(request, numero_destino):
    mensaje = "¡Hola desde Django con WhatsApp API! 🎉"
    url = f"https://graph.facebook.com/v22.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": mensaje}
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    # response = requests.post(url, headers=headers, json=data)
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # return JsonResponse(response.json())
    return HttpResponse("OK", status=200)

# views.py

@csrf_exempt
def webhook_whatsapp(request):
    if request.method == 'GET':
        # Meta valida el webhook por querystring.
        # El verify token debe ser propio y no el token de acceso.
        verify_token = (
            os.getenv("WHATSAPP_VERIFY_TOKEN")
            or getattr(settings, 'WHATSAPP_VERIFY_TOKEN', None)
            or settings.WHATSAPP_TOKEN
        )
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            return HttpResponse(challenge)
        else:
            return HttpResponse(status=403)

    if request.method == 'POST':
        # Seguridad: solo se aceptan eventos firmados por Meta
        firma_ok, motivo = _firma_meta_valida(request)
        if not firma_ok:
            logger.warning(
                'Webhook WhatsApp rechazado desde %s: %s',
                request.META.get('REMOTE_ADDR'), motivo
            )
            return JsonResponse({'error': 'Firma de Meta inválida'}, status=403)

        data = json.loads(request.body)
        # Aquí puedes procesar los mensajes o eventos
        entry = data["entry"][0]
        changes = entry["changes"][0]["value"]
        mensajes = changes.get("messages", [])

        if mensajes:
            mensaje = mensajes[0]
            texto = mensaje["text"]["body"]
            numero = mensaje["from"]
            print(f"📩 Mensaje de {numero}: {texto}")
            # Aquí puedes enviar una respuesta si lo deseas
        print("📨 Evento recibido:", json.dumps(data, indent=2))
        return HttpResponse(status=200)


# Ejemplo de uso
if __name__ == "__main__":
    enviar_mensaje(None, "593987468590")  # Reemplaza con el número de destino real