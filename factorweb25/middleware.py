import logging
import time
import uuid

from .request_context import request_id_context


logger = logging.getLogger("factorweb.request")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.request_id = request_id
        token = request_id_context.set(request_id)
        started = time.monotonic()

        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Unhandled request exception",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": 500,
                    "user_id": self._user_id(request),
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                },
            )
            request_id_context.reset(token)
            raise

        try:
            response["X-Request-ID"] = request_id
            extra = {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "user_id": self._user_id(request),
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            }
            if response.status_code >= 500:
                logger.error("Request completed with server error", extra=extra)
            elif response.status_code >= 400:
                logger.warning("Request completed with client error", extra=extra)
            else:
                logger.info("Request completed", extra=extra)
            return response
        finally:
            request_id_context.reset(token)

    @staticmethod
    def _user_id(request):
        user = getattr(request, "user", None)
        return user.pk if getattr(user, "is_authenticated", False) else None