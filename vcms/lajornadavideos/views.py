# -*- coding: utf-8 -*- #
from cacheback.queryset import QuerySetGetJob, QuerySetFilterJob
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from haystack.generic_views import SearchView

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

    results_per_page = 5

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        context.update({ 'home': HOME, 'activo': True })
        return context


class SeccionView(BaseView):

    template_name = 'pagina.html'

    def dispatch(self, request, *args, **kwargs):
        self.pagina = QuerySetGetJob(Pagina).get(slug=kwargs['seccion_slug'])
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class HomeView(SeccionView):

    def dispatch(self, request, *args, **kwargs):
        self.pagina = HOME
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class ListaView(SeccionView):

    template_name = 'lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.listado = {
            'lista': QuerySetGetJob(Lista).get(slug=kwargs['lista_slug']),
            'mostrar_nombre': True,
            'mostrar_descripcion': True,
            'mostrar_paginacion': True,
            'num_videos': 24,
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


class VideoView(PlayerView):

    template_name = 'video.html'



def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {}, content_type='application/xml')
