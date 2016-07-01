"""lajornadavideos URL Configuration"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.cache import cache_page

from .views import SeccionView, HomeView, VideoView, crossdomain

urlpatterns = [
    url(r'^$', cache_page(30)(HomeView.as_view()),
        name='home'),
    url(r'^secciones/(?P<seccion_slug>.+)/$',
        cache_page(30)(SeccionView.as_view()),
        name='seccion'),
    url(r'^video/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60)(VideoView.as_view()),
        name='video'),

    url(r'^busqueda/', include('haystack.urls')),

    url(r'^crossdomain\.xml$', crossdomain),
    url(r'^crossadomain\.xml$', crossdomain, name='busqueda'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
