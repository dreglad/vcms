# -*- coding: utf-8 -*- #
"""vcms URL Configuration"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView

from vcms import views
from vcms.api import router

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/videos/video/'), name='vcms_home'),
    url(r'^', include(admin.site.urls)),

    url(r'^salmonella/', include('salmonella.urls')),

    # API
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),

    # videos
    url(r'^video/status/(?P<video_pk>\d+)/',
        views.VideoStatusView.as_view(),
        name='procesamiento_status'
    ),
    url(r'^video/(?P<video_uuid>\d+)/(?P<video_slug>.+)/$',
        views.VideoRedirectView.as_view(),
        name='video'
    ),

    # suit integrations
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^select2/', include('django_select2.urls')),

    url(r'^crossdomain\.xml$', views.crossdomain),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def can_show_toolbar(request):
    return False
    return settings.DEBUG

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
