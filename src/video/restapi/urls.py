# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from piston.resource import Resource
from video.restapi.handlers import  *
from django.views.decorators.cache import cache_control

def cached_resource(maxage = 600):
    return cache_control(must_revalidate=True, public=True, max_age=maxage, s_maxage=maxage*2)

clip_handler = Resource(ClipHandler)
categoria_hanlder = Resource(CategoriaHanlder)
programa_hanlder = Resource(ProgramaHanlder)
tipo_clip_hanlder = Resource(TipoClipHandler)
tipo_programa_handler = Resource(TipoProgramaHandler)
pais_handler = Resource(PaisHandler)
tema_handler = Resource(TemaHandler)
corresponsal_handler = Resource(CorresponsalHandler)


urlpatterns = [
   #(r'^player/', include('player.urls')),

   url(r'^clip/(?P<slug>[^/]+)/$', cached_resource(60*10)(clip_handler)),
   url(r'^clip/(?P<slug>[^/]+)$', cached_resource(60*10)(clip_handler)),
   url(r'^clip/$', cached_resource(60*2)(clip_handler)),
   url(r'^clip/(?P<relacionados>relacionados)/(?P<slug>[^/]+)/', cached_resource(60*60*2)(clip_handler)),

   url(r'^categoria/(?P<slug>[^/]+)/', cached_resource(60*60*24)(categoria_hanlder)),
   url(r'^categoria/$', cached_resource(60*60*6)(categoria_hanlder)),

   url(r'^programa/(?P<slug>[^/]+)/', cached_resource(60*60*6)(programa_hanlder)),
   url(r'^programa/$', cached_resource(60*60*3)(programa_hanlder)),

   url(r'^tipo_clip/(?P<slug>[^/]+)/', cached_resource(60*60*12)(tipo_clip_hanlder)),
   url(r'^tipo_clip/$', cached_resource(60*60*6)(tipo_clip_hanlder)),

   url(r'^tipo_programa/(?P<slug>[^/]+)/', cached_resource(60*60*12)(tipo_programa_handler)),
   url(r'^tipo_programa/$', cached_resource(60*60*6)(tipo_programa_handler)),

   url(r'^tema/(?P<slug>[^/]+)/', cached_resource(60*60*24)(tema_handler)),
   url(r'^tema/$', cached_resource(60*60*24)(tema_handler)),

   url(r'^corresponsal/(?P<slug>[^/]+)/', cached_resource(60*60*3)(corresponsal_handler)),
   url(r'^corresponsal/$', cached_resource(60*30)(corresponsal_handler)),

   url(r'^pais/(?P<slug>[^/]+)/', cached_resource(60*60*6)(pais_handler)),
   url(r'^pais/$', cached_resource(60*60*6)(pais_handler)),

]
