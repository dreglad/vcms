# -*- coding: utf-8 -*- #
from cacheback.queryset import QuerySetGetJob, QuerySetFilterJob
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from haystack.generic_views import SearchView

from videos.models import *



DAYS = 86400; MINUTES = 60; HOURS = 3600
HOME = QuerySetGetJob(Pagina).get(slug='home'), lifetime=1*DAYS)


class BaseView(TemplateView):

    paginas = QuerySetFilterJob(Pagina).filter(activo=True, lifetime=1*HOURS)

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
            'lista': QueryGetFilterJob(Lista).get(slug=kwargs['lista_slug']),
            'mostrar_nombre': True,
            'mostrar_descripcion': True,
            'mostrar_paginacion': True,
            'num_videos': 24,
        }
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class PlayerView(BaseView):

    template_name = 'player.html'

    def dispatch(self, request, *args, **kwargs):
        self.video = self.get_video(kwargs['video_uuid'])
        if self.video.slug != kwargs['video_slug']:
            return redirect(video, permanent=True)

        self.player = request.GET.get('player', settings.DEFAULT_PLAYER)
        return super(WebPlayerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PlayerView, self).get_context_data(**kwargs)
        context.update({
            'player': self.player,
            'video': self.video,
        })
        return context


class VideoView(WebPlayerView):

    template_name = 'video.html'



def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {}, content_type='application/xml')
