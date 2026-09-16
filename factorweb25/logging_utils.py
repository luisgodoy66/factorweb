import json
import logging
from datetime import datetime, timezone

from .request_context import get_request_id


class JsonFormatter(logging.Formatter):
    """Formato estructurado para stdout, compatible con Docker y agregadores."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key in ("method", "path", "status", "duration_ms", "user_id", "integration"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        return json.dumps(payload, ensure_ascii=False, default=str)