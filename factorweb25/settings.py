from pathlib import Path
import os   
import locale
locale.setlocale(locale.LC_TIME, '')
# from decouple import config
# # 06-ene-23 l.g.    cambiar de decouple a dotenv
# 09-ene-23 l.g.    usar environ y el archivo de configuracion de elasticbeanstalk
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-o!$b%i-r8^9lc(0v7%rugi*dmy+!rumaxw)&o#1j7212*bxv1)'
# SECRET_KEY = config("SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
# SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
# Para producción, es crucial poner DEBUG en False
DEBUG = True
# ALLOWED_HOSTS = ['factorweb-dev2.us-east-2.elasticbeanstalk.com','localhost', '*']
# CSRF_TRUSTED_ORIGINS=['http://factorweb-dev2.us-east-2.elasticbeanstalk.com/']
# # ALLOWED_HOSTS = ['factorweb-dev.us-east-2.elasticbeanstalk.com','localhost', '127.0.0.1','*']
# # CSRF_TRUSTED_ORIGINS=['http://factorweb-dev.us-east-2.elasticbeanstalk.com/']
ALLOWED_HOSTS = [
    '69.62.68.116', 'localhost','127.0.0.1',
    'www.margarita.codigobambuecuador.com', # Reemplaza con tu dominio
    'margarita.codigobambuecuador.com', # Reemplaza con tu dominio
    # '*' # Es una mala práctica de seguridad en producción
    ]
CSRF_TRUSTED_ORIGINS=[
    'http://69.62.68.116',
    'https://69.62.68.116',
    'https://margarita.codigobambuecuador.com' # Añade tu dominio con https
    ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bases.apps.BasesConfig',
    'clientes.apps.ClientesConfig',
    'empresa.apps.EmpresaConfig',
    'operaciones.apps.OperacionesConfig',
    'solicitudes.apps.SolicitudesConfig',
    'pais.apps.PaisConfig',
    'cobranzas.apps.CobranzasConfig',
    'storages',
    'cuentasconjuntas.apps.CuentasconjuntasConfig',
    'contabilidad.apps.ContabilidadConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'factorweb25.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'factorweb25.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME':  'factorwebdb',
#         'HOST':  'database-2.c5i2bulrjalv.us-east-2.rds.amazonaws.com',
#         'USER': 'postgres',
#         'PASSWORD':os.getenv("PASSWORD_BD"),
#         'PORT': 5432,
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  'postgres',
        'HOST':  '69.62.68.116',
        'USER': 'postgres',
        'PASSWORD':os.getenv("PASSWORD_BD"),
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'es-ec'

TIME_ZONE = 'America/Guayaquil'

USE_I18N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL ='/login/'

# --- HTTPS Settings ---
# Asegúrate que tu proxy (Nginx, ELB, etc.) envía este encabezado
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# --- Fin de HTTPS Settings ---

# # CONFIGURACION AWS
# DEFAULT_FILE_STORAGE="storages.backends.s3boto3.S3Boto3Storage"
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME="factorweb-bucket"
# AWS_S3_CUSTOM_DOMAIN="%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
# AWS_S3_FILE_OVERWRITE = False
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
# STORAGES = {
#    "default": {
#         "BACKEND" : "storages.backends.s3boto3.S3StaticStorage",
#     },

#     "staticfiles":  {
#         "BACKEND" : "storages.backends.s3boto3.S3StaticStorage",
#     },
# }

# estaticos en la carpeta del proyecto
STATIC_URL = 'static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR,'static'),)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_ROOT = '/var/www/uploads'
MEDIA_URL = '/uploads/'

# Configuración de Google OAuth2
GOOGLE_OAUTH2_REDIRECT_URI = 'https://margarita.codigobambuecuador.com/api/google/oauth2callback/'  # MUST match your Authorized redirect URI

