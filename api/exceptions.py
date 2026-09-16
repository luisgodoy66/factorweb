import logging

from rest_framework.views import exception_handler

from factorweb25.request_context import get_request_id


logger = logging.getLogger("factorweb.api")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get("request")

    if response is None:
        logger.error(
            "Unhandled API exception",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={
                "method": getattr(request, "method", None),
                "path": getattr(request, "path", None),
                "status": 500,
            },
        )
        return None

    code = getattr(exc, "default_code", "api_error")
    details = response.data
    response.data = {
        "error": {
            "code": str(code),
            "message": "La solicitud no pudo procesarse.",
            "details": details,
            "request_id": get_request_id(),
        }
    }
    return response