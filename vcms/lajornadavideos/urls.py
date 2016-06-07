"""lajornadavideos URL Configuration"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.cache import cache_page

from .views import BusquedaView, CategoriaView, HomeView, VideoView, \
                   crossdomain

urlpatterns = [
    url(r'^$',
        HomeView.as_view(),
        name='home'),

    url(r'^secciones/(?P<categoria_slug>.+)/$',
        cache_page(60 * 15)(CategoriaView.as_view()),
        name='categoria'),

    url(r'^video/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60 * 15)(VideoView.as_view()),
        name='video'),

    url(r'^busqueda/$',
        cache_page(60 * 15)(BusquedaView.as_view()),
        name='busqueda'),

    url(r'^crossdomain\.xml$', crossdomain),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]