from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
import hmac
import json
import logging
from django.http import JsonResponse
from bases.models import Empresas, User
from .servicios import procesar_mensaje_del_agente

logger = logging.getLogger(__name__)


def _clave_webhook_valida(request):
    """Valida la clave compartida del webhook de carga de solicitudes.

    El agente (n8n) debe enviar la cabecera X-Margarita-Key con el valor de
    la variable de entorno MARGARITA_API_KEY.

    Si MARGARITA_API_KEY no esta definida, se rechaza la peticion: el webhook
    crea operaciones de factoring y no puede quedar abierto.
    """
    clave_esperada = getattr(settings, 'MARGARITA_API_KEY', None)
    if not clave_esperada:
        return False, 'MARGARITA_API_KEY no configurada en el entorno'

    clave_recibida = (
        request.headers.get('X-Margarita-Key')
        or request.POST.get('api_key')
        or ''
    )
    if not clave_recibida:
        return False, 'falta la cabecera X-Margarita-Key'

    if not hmac.compare_digest(str(clave_esperada), str(clave_recibida)):
        return False, 'clave invalida'
    return True, 'ok'


@csrf_exempt
@require_POST

def webhook_cargar_solicitudes_factoring(request):
    """Endpoint para que un agente IA envíe un correo ya leído y sus adjuntos XML para cargar solicitudes."""
    clave_ok, motivo = _clave_webhook_valida(request)
    if not clave_ok:
        logger.warning(
            'Webhook de solicitudes rechazado desde %s: %s',
            request.META.get('REMOTE_ADDR'), motivo
        )
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except json.JSONDecodeError:
            data = {}
    else:
        data = request.POST.dict()
        print(f"Webhook recibido con payload (form-data): ")
    correo_data = data.get('correo') or data.get('email') or data.get('message') or data.get('payload') or {}
    if isinstance(correo_data, str):
        try:
            print(f"Intentando decodificar correo_data desde string: {correo_data}")
            correo_data = json.loads(correo_data)
        except json.JSONDecodeError:
            correo_data = {}
    if not isinstance(correo_data, dict):
        return JsonResponse({'ok': False, 'error': 'El payload debe incluir un objeto correo o payload'}, status=400)

    empresa_id = data.get('empresa_id') or correo_data.get('empresa_id')
    user_id = data.get('user_id') or correo_data.get('user_id')
    dias = data.get('dias') or correo_data.get('dias')

    empresa = Empresas.objects.filter(id=empresa_id).first() if empresa_id else Empresas.objects.first()
    if empresa is None:
        return JsonResponse({'ok': False, 'error': 'No existe una empresa configurada'}, status=400)

    user = User.objects.filter(id=user_id).first() if user_id else User.objects.filter(is_superuser=True).first() or User.objects.first()
    if user is None:
        return JsonResponse({'ok': False, 'error': 'No existe un usuario para registrar las solicitudes'}, status=400)

    try:
        resultado = procesar_mensaje_del_agente(
            correo_data=correo_data,
            empresa=empresa,
            user=user,
            tipo_factoring=None,
            xsd_path=None,
            dias=dias
        )
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)
    # print(resultado)
    return JsonResponse({
        'ok': True,
        'empresa_id': empresa.id,
        'procesados': resultado.get('procesados', 0),
        'creadas': resultado.get('creadas', 0),
        # 'resultados': resultado.get('resultados', []),
        'correos': resultado.get('correos', []),
    })
'''
    ejemplo de payload que envia el agente IA:
{
  "correo": {
    "from": "facturas@example.com",
    "subject": "Factura nueva",
    "attachments": [
      {
        "filename": "factura.xml",
        "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><factura>...</factura>"
      }
    ]
  },
  "empresa_id": 1,
  "user_id": 1
}
'''

