# -*- coding: utf-8 -*- #
"""
vcms settings
"""
import os

from .menu import *

BASE_URL = 'http://videosadmin-stg.jornada.com.mx/'
BASE_FRONTEND_URL = 'http://videos-stg.jornada.com.mx/'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'storage'))
TEMP_ROOT = os.path.join(STORAGE_ROOT, 'tmp')

SECRET_KEY = 'd0^3t$7fwcp^6t!be^cu*14qrmNibzfi#58004@$u3@oiohshx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['videosadmin-stg.jornada.com.mx']


INSTALLED_APPS = [
    'suit',
    'suit_redactor',
    'suit_rq',
    'polymorphic',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #'cities_light',
    'corsheaders',
    'crispy_forms',
    'debug_toolbar',
    'django_countries',
    'django_rq',
    'django_select2',
    #'djsupervisor',
    'haystack',
    'locality',
    'mptt',
    'rest_framework',
    'reversion',
    'salmonella',
    'sorl.thumbnail',
    'taggit',

    'vcms.apps.VcmsVideosConfig',
]


CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'www.jornada.unam.mx',
    'jornada.com.mx',
    'videos.jornada.com.mx',
    'videos-stg.jornada.com.mx',
)


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600*48
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'vcms.settings.can_show_toolbar'
}

def can_show_toolbar(request):
    return False
    if request.is_ajax():
        return False
    return bool(DEBUG)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'file_log': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': '/var/log/vcms_error.log',
        },
        'file_debug': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/vcms_debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_debug', 'file_log'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'filters': [],
        },
        'vcms': {
            'handlers': ['file_debug', 'file_log'],
            'level': 'DEBUG',
            'filters': [],
        }
    },
}


MIDDLEWARE_CLASSES = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware'
]

ROOT_URLCONF = 'vcms.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'videos', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            # ],
        },
    },
]

WSGI_APPLICATION = 'vcms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'pass',
        'NAME': 'vcms'
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ['187.207.220.232', '127.0.0.1',]

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'es-MX'

LANGUAGES = ['es',]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale',)]

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(STORAGE_ROOT, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(STORAGE_ROOT, 'static', 'vcms')
STATICFILES_DIRS = [
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


CITIES_LIGHT_TRANSLATION_LANGUAGES = ['es']
#CITIES_LIGHT_INCLUDE_COUNTRIES = ['MX', 'US',]
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,

    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}


RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 3,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 3600,
    },
    'low': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 3,
    },
    'high': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 3,
    }
}
#RQ_EXCEPTION_HANDLERS = ['vcms.jobs.video.error_handler']

THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_REDIS_DB = 2
THUMBNAIL_KEY_PREFIX = 'vcms-thumbs'
THUMBNAIL_PREFIX = 'backend-thumbs/'
THUMBNAIL_REDIS_PASSWORD = ''
THUMBNAIL_REDIS_HOST = 'localhost'
THUMBNAIL_PADDING_COLOR = "#000000"
THUMBNAIL_OPTIONS_DICT = {
    'figure': {
        'geometry': '500x334',
        'crop': 'center',
    }
}

try:
    from local_settings import *
except ImportError as e:
    pass
