# -*- coding: utf-8 -*- #
from cacheback.queryset import QuerySetGetJob, QuerySetFilterJob
from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet

from videos.models import *



DAYS = 86400; MINUTES = 60; HOURS = 3600
try:
    HOME = QuerySetGetJob(Pagina, lifetime=1*DAYS).get(slug='home')
except Pagina.DoesNotExist:
    HOME = Pagina.objects.create(slug='home', nombre="Home", orden=0)


class BaseView(TemplateView):

    paginas = QuerySetFilterJob(Pagina, lifetime=1*HOURS).get(activo=True)

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)

        if self.request.is_ajax():
            context.update({
                'lista': QuerySetGetJob(Lista).get(
                            slug=self.request.GET.get('querystring_key')),
            })

        if hasattr(self, 'pagina'): context.update({ 'pagina': self.pagina })
        if hasattr(self, 'listado'): context.update({ 'listado': self.listado })
        context.update({ 'home': HOME, 'paginas': self.paginas })

        return context

    def get_template_names(self):
        """special AJAX lista case"""
        return self.request.is_ajax() and 'ajax_lista.html' or self.template_name


class BusquedaView(SearchView):

    results_per_page = 24

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        context.update({ 'home': HOME, 'activo': True })
        return context


class SeccionView(BaseView):

    template_name = 'pagina.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.pagina = QuerySetGetJob(Pagina).get(slug=kwargs['seccion_slug'])
        except Pagina.DoesNotExist:
            return redirect(HOME)
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class HomeView(SeccionView):

    def dispatch(self, request, *args, **kwargs):
        self.pagina = HOME
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class ListaView(SeccionView):

    template_name = 'lista.html'

    def dispatch(self, request, *args, **kwargs):
        try: 
            lista = QuerySetGetJob(Lista).get(slug=kwargs['lista_slug'])
        except Lista.DoesNotExist:
            return redirect(HOME, permanent=True)

        self.listado = {
            'lista': lista,
            'mostrar_nombre': True,
            'mostrar_descripcion': True,
            'mostrar_paginacion': True,
            'mostrar_maximo': 24,
        }
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class ListaEmbedView(SeccionView):

    template_name = 'embed_lista.html'

    def dispatch(self, request, *args, **kwargs):
        try: 
            lista = QuerySetGetJob(Lista).get(slug=kwargs['lista_slug'])
        except Lista.DoesNotExist:
            return redirect(self.video, permanent=True)

        self.listado = {
            'lista': lista,
            'mostrar_nombre': request.GET.get('mostrar_nombre', False),
            'mostrar_descripcion': request.GET.get('mostrar_descripcion', False),
            'mostrar_paginacion': request.GET.get('mostrar_paginacion', False),
            'layout': request.GET.get('layout', None),
            'target': request.GET.get('target', '_top'),
            'mostrar_maximo': request.GET.get('mostrar_maximo', 24),
        }
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class PlayerView(BaseView):

    template_name = 'player.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            video_pk = int(kwargs['video_uuid'].split('0', 1)[1])
            self.video = QuerySetGetJob(
                Video, lifetime=10*MINUTES).get(pk=video_pk)
            #self.video = Video.objects.publicos().get(pk=video_pk)
            if self.video.estado != Video.ESTADO.publicado:
                raise ValueError
        except (ValueError, IndexError, Video.DoesNotExist):
            raise Http404("Video inexistente")

        if self.video.slug != kwargs['video_slug']:
            return redirect(self.video, permanent=True)

        self.player = request.GET.get('player', settings.DEFAULT_PLAYER)
        return super(PlayerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PlayerView, self).get_context_data(**kwargs)
        context.update({
            'player': self.player,
            'video': self.video,
        })
        return context


class TwitterCardView(PlayerView):

    template_name = 'twitter_card.html'


class SimilaresView(PlayerView):

    def render_to_response(self, context, **response_kwargs):
        playlist = [{
            'sources': [{'file': result.object.archivo.url, 'type': 'video/mp4'}],
            'image': result.object.imagen.url,
            'title': result.object.titulo,
        } for result in list(SearchQuerySet().more_like_this(self.video)[:9])]

        return JsonResponse(playlist, safe=False, **response_kwargs)


class VideoView(PlayerView):

    template_name = 'video.html'


def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {}, content_type='application/xml')
