"""Settings para probar los servicios de correo de liquidacion.

Incluye las apps que intervienen en la cadena
solicitudes -> operaciones -> empresa.correos -> reportes y desactiva las
migraciones (que no aplican sobre SQLite) para crear el esquema desde los
modelos.
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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bases.apps.BasesConfig',
    'pais.apps.PaisConfig',
    'empresa.apps.EmpresaConfig',
    'clientes.apps.ClientesConfig',
    'solicitudes.apps.SolicitudesConfig',
    'operaciones.apps.OperacionesConfig',
    # api es importado por solicitudes.models (Configuracion_slack) y por
    # cobranzas.models (Configuracion_twilio_whatsapp), asi que sus modelos
    # deben estar registrados.
    'cobranzas.apps.CobranzasConfig',
    'contabilidad.apps.ContabilidadConfig',
    'cuentasconjuntas.apps.CuentasconjuntasConfig',
    'api.apps.ApiConfig',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'factorweb25.middleware.TenantMiddleware',
    'factorweb25.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'factorweb25.test_urls'

MIGRATION_MODULES = {
    'bases': None,
    'pais': None,
    'empresa': None,
    'clientes': None,
    'solicitudes': None,
    'operaciones': None,
    'cobranzas': None,
    'contabilidad': None,
    'cuentasconjuntas': None,
    'api': None,
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

MARGARITA_API_KEY = 'clave_global_de_prueba'
INTERNAL_API_KEY = 'clave_interna_de_prueba'
FIELD_ENCRYPTION_KEY = 'lSWs8YUvwIC_w1DVpvPGwjiyuQHBeDRKIeYn2ag8Ovw='
