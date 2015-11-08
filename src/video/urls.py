from django.conf.urls import include, url
from django.contrib import admin
from api import router


urlpatterns = [
    # Examples:
    # url(r'^$', 'vvv.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/django-rq/', include('django_rq.urls')),

    # API v1
    url(r'^api/v1/', include('video.restapi.urls')),

    # API v2
    url(r'^api/v2-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v2-docs/', include('rest_framework_swagger.urls')),
    url(r'^api/v2/', include(router.urls)),

    # admin-videos
    url(r'^admin/', include(router.urls)),
    url(r'admin/user_info/', 'video.views.user_info'),

    # ops
    url(r'^ops/crear/', 'video.views.crear_nuevo'),
    url(r'^ops/query_nuevo/', 'video.views.query_nuevo'),
    url(r'^ops/cambiar_thumbnail/', 'video.views.cambiar_thumbnail'),
    url(r'^ops/editar/', 'video.views.editar_clip'),
    url(r'^ops/publicar/', 'video.views.publicar_clip'),
    url(r'^ops/despublicar/', 'video.views.despublicar_clip'),
    url(r'^ops/eliminar/', 'video.views.eliminar_clip'),

    # frontend
    url(r'^player/(?P<clip_id>.+)/', 'video.views.player', name='player'),

    # crossdomain.xml
    url(r'^crossdomain\.xml', 'video.views.crossdomain'),
]
