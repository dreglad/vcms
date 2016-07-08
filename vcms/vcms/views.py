# -*- coding: utf-8 -*- #
import json
import os
import random

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.generic.base import RedirectView

from vcms.video_ops import extract_video_image
from videos.models import *


def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {},
                  content_type='application/xml')


def change_thumbnail_view(request):
    video = get_object_or_404(Video, pk=request.POST.get('id'))
    result = extract_video_image(
        video.archivo.path, video.imagen.path, autocrop=False,
        offset=video.duracion.total_seconds()*random.random()
        )
    return HttpResponse(json.dumps(result), content_type="application/json")


class VideoStatusView(View):
    def get(self, request, video_pk):
        video = get_object_or_404(Video, pk=video_pk)
        return HttpResponse(json.dumps(video.procesamiento_status),
                            content_type="application/json")

    def post(self, request, video_pk):
        video = get_object_or_404(Video, pk=video_pk)
        return HttpResponse(json.dumps(video.procesamiento_status),
                            content_type="application/json")


class VideoRedirectView(RedirectView):
    def get_redirect_url(*args, **kwargs):
        if settings.FRONTEND_URL:
            return '%svideo/%s/%s/' % (
                settings.FRONTEND_URL, kwargs['video_uuid'],
                kwargs['video_slug'],
                )
