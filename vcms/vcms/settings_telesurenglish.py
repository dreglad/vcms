# -*- coding: utf-8 -*- #
"""
vcms - telesuenglish settings
"""

DEBUG = True

PROJECT = 'telesurenglish'
SITE_NAME = 'Videos teleSUR English'
STORAGE_DIR = '/mnt/telesurenglish_storage'
RQ_QUEUES_DB = 8
THUMBNAIL_REDIS_DB = 13

exec open('/vagrant/vcms/vcms/settings.conf') in globals()

# Override ...
FRONTEND_URL = 'http://telesurenglish.openmultimedia.biz'
LANGUAGE_CODE = 'en'
LANGUAGES = ['en',]

# -*- coding: utf-8 -*- #
SUIT_CONFIG = {
    'MENU': (
        {'label': u'Contents', 'icon': 'icon-film',
         'app': 'videos', 'models': ('video', 'pagina', 'link')},

        {'label': u'Lists', 'icon': 'icon-tags',
         'app': 'videos', 'models': ('clasificador', 'lista')},

        {'label': u'Settings', 'icon': 'icon-cog',
         'models': ('auth.user', 'auth.group')},

        '-',

         {'label': 'Job queues', 'icon': 'icon-tasks',
         'url': '/django-rq/' }

        #{'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    ),
    # header
    'ADMIN_NAME': 'teleSUR English - Videos',
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
    from settings_telesurenglish_local import *
except ImportError as e:
    pass
