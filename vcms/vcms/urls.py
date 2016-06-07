# -*- coding: utf-8 -*- #
"""vcms URL Configuration
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework import routers

from . import views
import signals

router = routers.DefaultRouter()
router.register(r'videos', views.VideoViewSet)
router.register(r'autores', views.AutorViewSet)
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'tipos', views.TipoViewSet)
router.register(r'listas', views.ListaViewSet)
router.register(r'sitios', views.SitioViewSet)

urlpatterns = [
    # Admin
    url(r'^$', RedirectView.as_view(url='/videos/video/'), name='vcms_home'),

    url(r'^', include(admin.site.urls)),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
        ),

    url(r'^video/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        views.VideoRedirectView.as_view(),
        name='video'
        ),

    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^select2/', include('django_select2.urls')),

    url(r'^query/(?P<video_pk>\d+)/', views.query_nuevo_view, name='query_procesamiento'),

    # API v1
    # url(r'^api/v1-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^api/v1/', include(router.urls)),

    # ops
    # url(r'^ops/crear/$', views.crear_nuevo),
    # url(r'^ops/query_nuevo/$', views.query_nuevo),
    # url(r'^ops/cambiar_thumbnail/$', views.cambiar_thumbnail),
    # url(r'^ops/editar/$', views.editar_video),
    # url(r'^ops/publicar/$', views.publicar_video),
    # url(r'^ops/despublicar/$', views.despublicar_video),
    # url(r'^ops/eliminar/$', views.eliminar_video),

    # frontend
    # crossdomain.xml
    url(r'^crossdomain\.xml$', views.crossdomain),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
