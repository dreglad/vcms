"""lajornadavideos URL Configuration"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap, index
from django.views.decorators.cache import cache_page

from .sitemaps import VideoSitemap
from .views import \
    BusquedaView, HomeView, ListaEmbedView, PaginaView, PlayerView, \
    VideoView, SimilaresView, TwitterCardView

urlpatterns = [
    url(r'^$', cache_page(30)(HomeView.as_view()),
        name='home'),

    url(r'^video/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60*60)(VideoView.as_view()),
        name='video'),

    url(r'^secciones/(?P<seccion_slug>.+)/$',
        cache_page(30)(SeccionView.as_view()),
        name='seccion'),
    url(r'^listas/(?P<lista_slug>.+)/$',
        cache_page(30*2)(ListaView.as_view()),
        name='lista'),

    url(r'^busqueda/', cache_page(60*10)(BusquedaView.as_view()),
        name='haystack_search'),

    url(r'^lista_embed/(?P<lista_slug>.+)/$',
        cache_page(30*2)(ListaEmbedView.as_view()),
        name='lista'),
    url(r'^pplayer/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60*60)(PlayerView.as_view()),
        name='video_player'),
    url(r'^twitter_card/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(120)(TwitterCardView.as_view()),
        name='twitter_card'),
    url(r'^similares/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60*60)(SimilaresView.as_view()),
        name='similares'),
    url(r'^player/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        cache_page(60)(PlayerView.as_view()),
        name='web_player'),

    url(r'^sitemap\.xml$', index,
        {'sitemaps': {'video': VideoSitemap }},
        name='sitemap_index'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {
            'sitemaps': {'video': VideoSitemap },
            'template_name': 'video_sitemap.xml',
        }, name='sitemap_section'),

    url(r'^busqueda/', cache_page(60*10)(BusquedaView.as_view()),
        name='haystack_search'),

    url(r'^robots\.txt', include('robots.urls')),

    url(r'^crossdomain\.xml$', cache_page(3600*24*30)(crossdomain)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
