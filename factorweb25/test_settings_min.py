"""Settings minimos para probar la autenticacion de webhooks.

Incluye solo las apps imprescindibles (bases, empresa y sus dependencias),
de modo que las migraciones de operaciones/cobranzas/contabilidad no se
ejecuten: esas no aplican sobre SQLite.

Uso:
    python manage.py test empresa.tests_seguridad \
        --settings=factorweb25.test_settings_min
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'factorweb25.middleware.TenantMiddleware',
    'factorweb25.middleware.RequestLoggingMiddleware',
]

# La suite invoca los helpers directamente con RequestFactory, sin resolver
# URLs. Se usa un URLconf vacio porque el real importa todas las vistas.
ROOT_URLCONF = 'factorweb25.test_urls'

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Las migraciones de estas apps dependen de otras apps (operaciones,
# cobranzas...) que no forman parte de esta suite y cuyas migraciones no
# aplican sobre SQLite. Al desactivarlas, Django crea las tablas a partir de
# los modelos con run_syncdb.
MIGRATION_MODULES = {
    'bases': None,
    'pais': None,
    'empresa': None,
}

# Credenciales deterministas para las pruebas.
MARGARITA_API_KEY = 'clave_global_de_prueba'
INTERNAL_API_KEY = 'clave_interna_de_prueba'
