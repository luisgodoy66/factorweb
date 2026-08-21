import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta

from operaciones.models import Documentos

@csrf_exempt
@require_POST
def facturas_por_vencer(request):
    """
    Recibe en el body (JSON): dias, empresa_id, usuario_id
    Devuelve un JSON con las facturas por vencer dentro del rango de días
    indicado, agrupadas por cliente.
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Body inválido, se espera JSON"}, status=400)

    dias = body.get("dias")
    empresa_id = body.get("empresa_id")
    usuario_id = body.get("usuario_id")

    if dias is None or empresa_id is None:
        return JsonResponse(
            {"error": "Se requieren los parámetros: dias, empresa_id"},
            status=400,
        )

    try:
        dias = int(dias)
    except (TypeError, ValueError):
        return JsonResponse({"error": "El parámetro dias debe ser numérico"}, status=400)

    if dias < 0:
        return JsonResponse({"error": "El parámetro dias no puede ser negativo"}, status=400)

    hoy = timezone.now().date()
    fecha_limite = hoy + timedelta(days=dias)

    facturas = (
        Documentos.objects.filter(
            empresa_id=empresa_id,
            leliminado=False,
            nsaldo__gt=0,
            cxasignacion__cxtipo="F",
            cxasignacion__cxestado="P",
            cxasignacion__leliminado=False,
            dvencimiento__lte=fecha_limite,
        )
        .select_related("cxcliente__cxcliente", "cxasignacion")
        .order_by("cxcliente__cxcliente__ctnombre", "dvencimiento")
    )

    clientes = {}
    for factura in facturas:
        fecha_vencimiento = factura.vencimiento()
        if not hoy <= fecha_vencimiento <= fecha_limite:
            continue

        cliente = factura.cxcliente.cxcliente
        if factura.cxcliente_id not in clientes:
            clientes[factura.cxcliente_id] = {
                "nombre": cliente.ctnombre,
                "celular": cliente.ctcelular,
                "facturas": [],
            }
        clientes[factura.cxcliente_id]["facturas"].append(
            {
                "numero": factura.ctdocumento,
                "fecha_vencimiento": fecha_vencimiento.isoformat(),
                "saldo": float(factura.nsaldo),
            }
        )

    resultado = list(clientes.values())

    return JsonResponse(
        {
            "empresa_id": empresa_id,
            "usuario_id": usuario_id,
            "dias": dias,
            "clientes": resultado,
        },
        status=200,
        safe=True,
    )
