# -*- coding: utf-8 -*- #
SUIT_CONFIG = {
    'MENU': (
        {'label': u'Videos', 'icon': 'icon-film',
         'app': 'videos', 'models': ('video', 'lista')},

        {'label': u'Categorización', 'icon': 'icon-tags',
         'app': 'videos', 'models': ('autor', 'categoria', 'tipo',)},
         
        {'app': 'auth', 'label': 'Control de acceso', 'icon': 'icon-lock',
         'models': ('user', 'group')},

        '-',

        {'label': u'Sitios', 'icon': 'icon-globe', 'url': '/videos/sitio/',},

        '-',
         
        {'label': u'Configuración', 'icon': 'icon-cog', 'url': '/django-rq/' },

         '-',
         
         {'label': 'Cola de trabajos', 'icon': 'icon-tasks',
         'url': '/django-rq/' }
        
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
