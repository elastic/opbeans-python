import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0k&#0n#m3hx!s8ue5aksa)cviu*2^bdg)hk(%z#&uk-q+mn27v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "db_prefix",
    'elasticapm.contrib.django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'opbeans',
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'elasticapm.contrib.django.middleware.TracingMiddleware',
    'elasticapm.contrib.django.middleware.Catch404Middleware',
    'opbeans.middleware.tag_request_id_middleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'opbeans.middleware.user_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'opbeans.urls'

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
                'opbeans.context_processors.rum_settings',
                'elasticapm.contrib.django.context_processors.rum_tracing',
            ],
        },
    },
]

WSGI_APPLICATION = 'opbeans.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, default='sqlite:///{}/demo/db.sql'.format(BASE_DIR))
}

DB_PREFIX = os.environ.get("DB_PREFIX", None)


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'opbeans', 'static', 'build', 'static')
ASSET_MANIFEST = os.path.join(BASE_DIR, 'opbeans', 'static', 'build', 'asset-manifest.json')
ELASTIC_APM = {
    "DEBUG": True,
    "SERVICE_NAME": os.environ.get('ELASTIC_APM_SERVICE_NAME', 'opbeans-python'),
    "TRANSACTION_SEND_FREQ": 5,
    "PROMETHEUS_METRICS": True,
}

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'update-stats': {
        'task': 'opbeans.tasks.update_stats',
        'schedule': 5,
        'args': (),
    },
    'sync_customers': {
        'task': 'opbeans.tasks.sync_customers',
        'schedule': 49,
        'args': (),
    },
    'sync_orders': {
        'task': 'opbeans.tasks.sync_orders',
        'schedule': 30,
        'args': (),
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL', 'redis://localhost:6379') + "/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "cache"
    }
}

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

import structlog

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': "json" if "ENABLE_JSON_LOGGING" in os.environ else "console",
        },
        'elasticapm': {
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
            'level': 'WARNING',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'opbeans': {
            'handlers': ['console', 'elasticapm'],
            'level': 'INFO',
        },
        'elasticapm': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}

structlog_processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso", key="@timestamp"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

try:
    from elasticapm.handlers.structlog import structlog_processor

    structlog_processors.insert(4, structlog_processor)
except ImportError:
    pass


structlog.configure(
    processors=structlog_processors,
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
