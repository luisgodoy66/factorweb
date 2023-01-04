from pathlib import Path
import os   
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-o!$b%i-r8^9lc(0v7%rugi*dmy+!rumaxw)&o#1j7212*bxv1)'
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['factorcloud2-dev.us-east-2.elasticbeanstalk.com','localhost', '127.0.0.1','*']
CSRF_TRUSTED_ORIGINS=['http://factorcloud2-dev.us-east-2.elasticbeanstalk.com/']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bases.apps.BasesConfig',
    'clientes.apps.ClientesConfig',
    'empresa.apps.EmpresaConfig',
    'operaciones.apps.OperacionesConfig',
    'solicitudes.apps.SolicitudesConfig',
    'pais.apps.PaisConfig',
    'cobranzas.apps.CobranzasConfig',
    'storages',
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

ROOT_URLCONF = 'factorweb.urls'

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

WSGI_APPLICATION = 'factorweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  'factorwebdb',
        'HOST':  'database-1.c5i2bulrjalv.us-east-2.rds.amazonaws.com',
        'USER': 'postgres',
        'PASSWORD':'milo2015',
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

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR,'static'),)
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL ='/login/'


# CONFIGURACION AWS
# AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY=config("AWS_SECRET_ACCESS_KEY")
AWS_ACCESS_KEY_ID ="AKIAUW2EOMCY6M7XEXND"
AWS_SECRET_ACCESS_KEY="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"

AWS_STORAGE_BUCKET_NAME="factorweb-bucket"

DEFAULT_FILE_STORAGE="storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE="storages.backends.s3boto3.S3Boto3Storage"

AWS_S3_CUSTOM_DOMAIN="%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False
ADMIN_MEDIA_PREFIX = '/static/admin/'