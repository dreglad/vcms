# -*- coding: utf-8 -*- #
"""
vcms - ojarasca settings
"""
import os

DEBUG = True

PROJECT = 'ojarasca'
SITE_NAME = 'Videos ojarasca'
STORAGE_DIR = '/mnt/ojarasca_storage'
RQ_QUEUES_DB = 3
THUMBNAIL_REDIS_DB = 3

exec open('/vagrant/vcms/vcms/settings.conf') in globals()

# Override ...
FRONTEND_URL = None
LANGUAGE_CODE = 'es'
LANGUAGES = ['es',]

SUIT_CONFIG = {
    'MENU': (
        {'label': u'Contenido', 'icon': 'icon-film',
         'app': 'videos', 'models': ('video',)},

        {'label': u'Listas', 'icon': 'icon-tags',
         'app': 'videos', 'models': ('clasificador', 'lista')},

        {'label': u'Configuración', 'icon': 'icon-cog',
         'models': ('auth.user', 'auth.group')},

        '-',

         {'label': 'Cola de trabajos', 'icon': 'icon-tasks',
         'url': '/django-rq/' }

        #{'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    ),
    # header
    'ADMIN_NAME': 'Videos | Micrositio ojarasca',
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
    from settings_ojarasca_local import *
except ImportError as e:
    pass
