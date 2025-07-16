# views.py
import requests
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

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
        # Meta valida el webhook por querystring
        verify_token = settings.WHATSAPP_TOKEN  # Define tú este token
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            return HttpResponse(challenge)
        else:
            return HttpResponse(status=403)

    if request.method == 'POST':
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