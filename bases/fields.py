from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _get_fernet():
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not key:
        raise ImproperlyConfigured(
            'FIELD_ENCRYPTION_KEY no está configurada. Genere una con '
            '`Fernet.generate_key()` y agréguela a las variables de entorno.'
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedTextField(models.TextField):
    """TextField cifrado en reposo con Fernet (AES-128-CBC + HMAC-SHA256).

    Los valores previos sin cifrar (datos heredados) se leen tal cual, ya
    que Fernet no puede desencriptarlos y se detecta por InvalidToken.
    """

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return _get_fernet().encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            return value
