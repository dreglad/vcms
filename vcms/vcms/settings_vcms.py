# -*- coding: utf-8 -*- #
"""
vcms - lajornadavideos settings
"""

DEBUG = False

PROJECT = 'vcms'
SITE_NAME = 'Videos La Jornada'
STORAGE_DIR = '/mnt/vcms_storage'
RQ_QUEUES_DB = 3
THUMBNAIL_REDIS_DB = 11

exec open('/vagrant/vcms/vcms/settings.conf') in globals()

# Override ...
FRONTEND_URL = 'http://videos-stg.jornada.com.mx/'
LANGUAGE_CODE = 'es'
LANGUAGES = ['es',]

SUIT_CONFIG = {
    'CONFIRM_UNSAVED_CHANGES': False,
    'MENU': (
        {'label': u'Contenido', 'icon': 'icon-film',
         'app': 'videos', 'models': ('video','pagina', 'link')},

        {'label': u'Listas', 'icon': 'icon-tags',
         'app': 'videos', 'models': ('clasificador', 'lista')},

        {'label': u'Configuración', 'icon': 'icon-cog',
         'models': ('videos.plataforma', 'auth.user', 'auth.group')},

        '-',

        {'label': 'Autores', 'icon': 'icon-tasks',
         'url': '/videos/lista/?q=&clasificador=autor' },
        {'label': 'Formatos', 'icon': 'icon-tasks',
         'url': '/videos/lista/?q=&clasificador=formato' },
        {'label': 'Series', 'icon': 'icon-tasks',
         'url': '/videos/lista/?q=&clasificador=serie' },
        {'label': 'Secciones', 'icon': 'icon-tasks',
         'url': '/videos/lista/?q=&clasificador=seccion' },

         '-',
         '-',
         '-',

        {'label': 'Cola de trabajos', 'icon': 'icon-tasks',
         'url': '/django-rq/' },

        #{'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    ),
    # header
    'ADMIN_NAME': 'Videos | La Jornada',
    'HEADER_DATE_FORMAT': 'l, j \d\e F \d\e Y',
    'HEADER_TIME_FORMAT': 'H:i',

    # forms
    # 'SHOW_REQUIRED_ASTERISK': True,  # Default True
    # 'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    'SEARCH_URL': '',

    'MENU_EXCLUDE': ('taggit',),
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    # 'LIST_PER_PAGE': 15
}


try:
    from settings_wikileaks_local import *
except ImportError as e:
    pass
