# -*- coding: utf-8 -*- #
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic.base import TemplateView

from videos.models import *


class BaseView(TemplateView):
    home = Pagina.objects.get(slug='home', activo=True)
    paginas = Pagina.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        if hasattr(self, 'pagina'):
            context.update({
                'pagina': self.pagina,
            })
        context.update({
            'home': self.home,
            'paginas': self.paginas,
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
