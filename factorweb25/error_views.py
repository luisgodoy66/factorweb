from django.http import JsonResponse

from .request_context import get_request_id


def _is_api_request(request):
    return request.path.startswith("/api/") or "application/json" in request.headers.get(
        "Accept", ""
    )


def _error_response(request, status, code, message):
    request_id = get_request_id() or getattr(request, "request_id", None)
    if _is_api_request(request):
        return JsonResponse(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "request_id": request_id,
                }
            },
            status=status,
        )
    return JsonResponse({"error": message, "request_id": request_id}, status=status)


def bad_request(request, exception=None):
    return _error_response(request, 400, "bad_request", "La solicitud no es válida.")


def permission_denied(request, exception=None):
    return _error_response(request, 403, "permission_denied", "No tiene permisos para esta operación.")


def not_found(request, exception=None):
    return _error_response(request, 404, "not_found", "El recurso solicitado no existe.")


def server_error(request):
    return _error_response(request, 500, "internal_error", "Ocurrió un error interno.")