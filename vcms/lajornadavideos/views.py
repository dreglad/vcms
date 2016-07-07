# -*- coding: utf-8 -*- #
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic.base import TemplateView
from haystack.generic_views import SearchView

from videos.models import *



class BaseView(TemplateView):
    home = Pagina.objects.get(slug='home', activo=True)
    paginas = Pagina.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)

        if self.request.is_ajax():
            context.update({
                'lista': Lista.objects.get(
                    slug=self.request.GET.get('querystring_key')),
            })

        if hasattr(self, 'pagina'):
            context.update({
                'pagina': self.pagina,
            })
        if hasattr(self, 'listado'):
            context.update({
                'listado': self.listado,
            })
        context.update({
            'home': self.home,
            'paginas': self.paginas,
        })
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return 'ajax_lista.html'
        else:
            return self.template_name




class BusquedaView(SearchView):
    # def extra_context(self):
    #     return {
    #         'home': Pagina.objects.get(slug='home', activo=True),
    #     }

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        context.update({
            'home': Pagina.objects.get(slug='home', activo=True),
        })
        return context


class SeccionView(BaseView):
    template_name = "seccion.html"

    def dispatch(self, request, *args, **kwargs):
        self.pagina = get_object_or_404(Pagina, slug=kwargs['seccion_slug'])
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class HomeView(SeccionView):
    def dispatch(self, request, *args, **kwargs):
        self.pagina = self.home
        return super(SeccionView, self).dispatch(request, *args, **kwargs)


class ListaView(SeccionView):

    template_name = "lista.html"

    def dispatch(self, request, *args, **kwargs):
        self.listado = {
            'lista': get_object_or_404(Lista, slug=kwargs['lista_slug']),
            'mostrar_nombre': True,
            'mostrar_descripcion': True,
            'mostrar_paginacion': True,
            'num_videos': 24,
        }
        return super(SeccionView, self).dispatch(request, *args, **kwargs)



class VideoView(BaseView):

    template_name = "video.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            video_pk = int(kwargs['video_uuid'].split('0', 1)[1])
            self.video = Video.objects.publicos().get(pk=video_pk)
        except (ValueError, IndexError, Video.DoesNotExist):
            raise Http404("Video inexistente")

        if self.video.uuid != kwargs['video_uuid']:
            raise Http404("Video inexistente")
        if self.video.slug != kwargs['video_slug']:
            return redirect(video, permanent=True)

        self.player = request.GET.get('player', 'jwplayer')

        return super(VideoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VideoView, self).get_context_data(**kwargs)

        context.update({
            'player': self.player,
            'video': self.video,
            'relacionados': Video.objects.publicos()[:24],
        })
        return context


def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {},
                  content_type='application/xml')
