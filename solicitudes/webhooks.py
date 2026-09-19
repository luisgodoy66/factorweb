from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
import json
import logging
from django.http import JsonResponse
from bases.models import Empresas, User
from empresa.claves import (
    NOMBRES_CABECERA_CLAVE,
    resolver_empresa_webhook,
    validar_clave_webhook,
)
from .servicios import procesar_mensaje_del_agente

logger = logging.getLogger(__name__)


def _clave_webhook_valida(request):
    """Valida la clave del webhook de carga de solicitudes.

    Admite las claves por empresa definidas en empresa.Claves_webhook y, por
    compatibilidad hacia atras, la clave global de entorno
    (MARGARITA_API_KEY / INTERNAL_API_KEY).

    Mantiene el contrato (bool, motivo) que ya usaban las pruebas.
    """
    _empresa_id, _clave, error = validar_clave_webhook(request)
    if error:
        return False, error
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

    # 16-sep-26 l.g.  'dias' puede llegar como numero (body JSON del agente) o
    # como texto ("30", body de formulario).  _crear_documento_desde_datos hace
    # timedelta(days=dias), que revienta con TypeError si llega un str o None,
    # por lo que se normaliza a entero y se usa 30 como valor por defecto.
    try:
        dias = int(data.get('dias') or correo_data.get('dias') or 30)
    except (TypeError, ValueError):
        logger.warning(
            'Webhook de solicitudes: valor de dias invalido (%r), se usan 30 dias',
            data.get('dias') or correo_data.get('dias')
        )
        dias = 30

    # La empresa se resuelve desde la clave: si la clave es de una empresa,
    # prevalece sobre el empresa_id del cuerpo (aislamiento multi-tenant).
    empresa, error_empresa = resolver_empresa_webhook(
        request, empresa_id if empresa_id else None)
    if error_empresa or empresa is None:
        empresa = empresa or Empresas.objects.first()
        if empresa is None:
            return JsonResponse(
                {'ok': False, 'error': 'No existe una empresa configurada'},
                status=400)
        logger.warning(
            'Webhook de solicitudes: %s; se usa la empresa %s (%s) por defecto',
            error_empresa, empresa.id, empresa.ctnombre)

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
        'empresa': empresa.ctnombre,
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

