import datetime
import logging
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('secret_key')

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'app.apps.AppConfig',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'app.utils.auth_middleware.AuthenticationMiddlewareJWT'
]

ROOT_URLCONF = 'btk2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'btk2.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'btk2db',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

logging.basicConfig(
    level=logging.DEBUG,
    filename=f'{BASE_DIR}/app_log.log',
    filemode='a',
    format='%(levelname)s %(asctime)s %(funcName)s %(lineno)d: [%(message)s]',
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
)
CORS_ORIGIN_REGEX_WHITELIST = (
    'localhost:3000',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=86400)
}

# REDIS related settings
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'



