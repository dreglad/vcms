# -*- coding: utf-8 -*- #
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic.base import TemplateView

from videos.models import *


class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context.update({ 'categorias': Categoria.objects.all() })
        if getattr(self, 'categoria', None):
            context.update({'categoria_actual': self.categoria })
        elif getattr(self, 'video', None):
            context.update({'categoria_actual': self.video.categoria })
        return context


class HomeView(BaseView):

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'videos': Video.objects.publicos()[:20],
            'listas': Lista.objects.destacados(),
        })
        return context


class CategoriaView(BaseView):

    template_name = "categoria.html"

    def dispatch(self, request, *args, **kwargs):
        self.categoria = get_object_or_404(Categoria,
                                           slug=kwargs['categoria_slug'])
        return super(CategoriaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoriaView, self).get_context_data(**kwargs)
        context.update({
            'listas': Lista.objects.destacados(self.categoria),
            'videos': list(Video.objects.publicos().filter(categoria=self.categoria)[:32]),
        })
        return context



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
        
        return super(VideoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VideoView, self).get_context_data(**kwargs)
        context.update({ 'video': self.video })
        return context


def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {},
                  content_type='application/xml')