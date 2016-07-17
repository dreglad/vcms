# -*- coding: utf-8 -*- #
""" lajornadavideos settings
"""
import os

BASE_URL = 'http://videos-dev.jornada.com.mx/'
BASE_BACKEND_URL = 'http://videosadmin-dev.jornada.com.mx/'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_ROOT = '/mnt/lajornadavideos_storage'
#TEMP_ROOT = os.path.join(STORAGE_ROOT, 'tmp')

SECRET_KEY = 'd0^3t$7fwcp^6t!be^9u*1kqrysibzfi#58004@$u3@oiohshx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'videos-stg.jornada.com.mx', 'videos-dev.jornada.com.mx',
]

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-80731325-1'

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    'analytical',
    'compressor',
    'el_pagination',
    'crispy_forms',
    'debug_toolbar',
    'django_countries',
    'haystack',
    'locality',
    'mptt',
    'rest_framework',
    'sorl.thumbnail',
    'taggit',

    'videos',
]


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


X_FRAME_OPTIONS = (
    'ALLOW-FROM http://www.jornada.unam.mx/ https://editonline.jornada.com.mx/ '
    'http://ojarasca.jornada.com.mx/ http://semanal.jornada.com.mx/ '
    'http://letraese.jornada.com.mx/ http://ciencias.jornada.com.mx/ '
    'http://wikileaks.jornada.com.mx/ http://staging.jornada.com.mx/'
)


CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600*48
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'lajornadavideos.settings.can_show_toolbar'
}

def can_show_toolbar(request):
    #return False
    return True
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
            'level': 'ERROR',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': '/var/log/vcms/lajornadavideos_error.log',
        },
        'file_debug': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/vcms/lajornadavideos_debug.log',
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
    #'django.middleware.cache.UpdateCacheMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
]

ROOT_URLCONF = 'lajornadavideos.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'lajornadavideos', 'templates'),
            os.path.join(BASE_DIR, 'videos', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                #'django.contrib.auth.context_processors.auth',
                #'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            # ],
        },
    },
]

WSGI_APPLICATION = 'lajornadavideos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'pass',
        'NAME': 'lajornadavideos'
    }
}

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack',
#     },
# }

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 12

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        #'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
         'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}

ELASTICSEARCH_INDEX_SETTINGS = {
    'settings': {
        "analysis": {
            "analyzer": {
                "synonym_analyzer" : {
                    "type": "custom",
                    "tokenizer" : "standard",
                    "filter" : ["synonym"]
                },
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "lowercase",
                    "filter": ["haystack_ngram", "synonym"]
                },
                "edgengram_analyzer": {
                    "type": "custom",
                    "tokenizer": "lowercase",
                    "filter": ["haystack_edgengram"]
                }
            },
            "tokenizer": {
                "haystack_ngram_tokenizer": {
                    "type": "nGram",
                    "min_gram": 3,
                    "max_gram": 15,
                },
                "haystack_edgengram_tokenizer": {
                    "type": "edgeNGram",
                    "min_gram": 2,
                    "max_gram": 15,
                    "side": "front"
                }
            },
            "filter": {
                "haystack_ngram": {
                    "type": "nGram",
                    "min_gram": 3,
                    "max_gram": 15
                },
                "haystack_edgengram": {
                    "type": "edgeNGram",
                    "min_gram": 2,
                    "max_gram": 15
                },
                "synonym" : {
                    "type" : "synonym",
                    "ignore_case": "true",
                    "synonyms_path" : "synonyms.txt"
                }
            }
        }
    }
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
STATIC_ROOT = os.path.join(STORAGE_ROOT, 'frontend_static')

STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'lajornadavideos', 'static') ]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


CITIES_LIGHT_TRANSLATION_LANGUAGES = ['es']
#CITIES_LIGHT_INCLUDE_COUNTRIES = ['MX', 'US',]
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]


COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
#COMPRESS_ENABLED = True

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
}

#THUMBNAIL_FORMAT = 'png'
THUMBNAIL_PRESERVE_FORMAT = True
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_KEY_PREFIX = 'lajornadavideos-thumbs'
THUMBNAIL_PREFIX = 'thumbs/'
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
