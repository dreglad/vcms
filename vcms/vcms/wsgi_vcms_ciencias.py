import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vcms.settings_ciencias")

application = get_wsgi_application()
