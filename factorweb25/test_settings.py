"""Settings para ejecutar la suite de tests sin tocar la base de produccion.

Uso:
    python manage.py test --settings=factorweb25.test_settings api.tests_seguridad

La base de datos se resuelve en SQLite en memoria, de modo que el runner de
Django nunca crea ni destruye nada en el servidor PostgreSQL de produccion.
"""
from .settings import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Los tests de webhooks necesitan construir la URL publica con host 'testserver'.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Credenciales deterministas para que las pruebas de firma y de clave
# no dependan de variables de entorno externas.
MARGARITA_API_KEY = os.getenv('MARGARITA_API_KEY', 'clave_de_prueba')  # noqa: F405
INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY', 'clave_interna_prueba')  # noqa: F405
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET', 'secreto_meta_de_prueba')  # noqa: F405

# Clave Fernet determinista para que los tests que usan EncryptedTextField no dependan del entorno.
FIELD_ENCRYPTION_KEY = os.getenv('FIELD_ENCRYPTION_KEY', 'lSWs8YUvwIC_w1DVpvPGwjiyuQHBeDRKIeYn2ag8Ovw=')  # noqa: F405
