# -*- coding: utf-8 -*- #
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
import json
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from clips.models import *
import urllib2
from datetime import datetime, time
from time import mktime
from subprocess import call, check_output, CalledProcessError
import random
from time import sleep
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import os
import uuid
import random
import redis
import json
import hashlib
from django.http import Http404


is_staff = lambda user: user.is_staff

def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {}, content_type='application/xml')


def player(request, clip_id):
    clip = get_object_or_404(Clip, pk=clip_id)
    return render(request, 'player.html', {'clip': clip})


@user_passes_test(is_staff)
def user_info(request):
    return HttpResponse(json.dumps({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        }), content_type="application/json")


@csrf_exempt
def cambiar_thumbnail(request):
    if request.POST.get('id'):
        clip = Clip.objects.get(pk=request.POST.get('id'))
    else:
        clip = Clip.objects.get(slug=request.POST.get('slug'))

    nombre_imagen = 'images/image-%s.png' % uuid.uuid4()
    temp_path = '/tmp/%s.png' % uuid.uuid4()
    offset = (clip.duracion.minute*60 + clip.duracion.second) * random.random()
    cmd_imagen = 'ffmpeg -y -ss %d -i %s -vcodec png -vframes 1 -an -f rawvideo %s' % (offset, clip.archivo.path, temp_path)
    call(cmd_imagen, shell=True)
    clip.imagen.save(nombre_imagen, ContentFile(open(temp_path, 'r').read()))

    if not clip.observaciones: clip.observaciones = ''
    clip.observaciones += u"\nThumbnail regenerado por %s desde Admin en %s" % (request.POST.get('usuario_remoto'), datetime.now().isoformat())

    clip.save()

    return HttpResponse('{"success": true, "id": %d }' % clip.id, content_type="application/json")



@csrf_exempt
def crear_nuevo(request):
    from video.jobs.ops import crear_nuevo_clip_job

    if request.POST.get('archivo_id'):
        status_path = settings.STORAGE_DIR + 'temp/status/%s.txt' % request.POST.get('archivo_id')
        with open(status_path, 'w') as status_file:
            status_file.write('queue')
            crear_nuevo_clip_job.delay(request.POST)
        success = True
    else:
        success = False

    return HttpResponse(json.dumps({"success": success}), content_type="application/json")


@csrf_exempt
def query_nuevo(request):
    archivo_id = request.GET.get('archivo_id')
    temp_path = settings.STORAGE_DIR + 'temp'
    status_path = '%s/status/%s.txt' % (temp_path, archivo_id)
    vstats_path = '%s/vstats_%s.txt' % (temp_path, archivo_id)

    result = {}

    if os.path.exists(status_path):
        with open(status_path, 'r') as status_file:
            status_list = status_file.read().split()

        result['status'] = status_list[0]

        if status_list[0] == 'download':
            # download has begun
            result['tries'] = status_list[1]
        elif status_list[0] == 'valid':
            # download has finished and compreession started
            result['total'] = float(status_list[1])
            try:
                vstats_line = check_output(['tail', '-2', vstats_path]).split("\n")[0]
                result['seconds'] = float(vstats_line.split()[9])
                result['progress'] = 100 * round(result['seconds'] / result['total'], 2)
            except (CalledProcessError, IndexError):
                # No vstats file or invalid
                result['seconds'] = 0
                result['progress'] = 0
        elif status_list[0] == 'done':
            result['id'] = int(status_list[1])
    else:
        # status file no existe
        result['status'] = None

    return HttpResponse(json.dumps(result), content_type="application/json")



@csrf_exempt
def editar_clip(request):
    if request.method != 'POST':
        raise Http404('Only POST allowed')

    if request.POST.get('id'):
        clip = Clip.objects.get(pk=request.POST.get('id'))
    else:
         clip = Clip.objects.get(slug=request.POST.get('slug'), idioma_original=request.POST.get('idioma', 'es'))

    if request.POST.get('archivo_img_id'):
        archivo_url = 'http://upload.openmultimedia.biz/files/%s' % request.POST.get('archivo_img_id')
        archivo_path = '/tmp/%s' % request.POST.get('archivo_img_id')
        webfile = urllib2.urlopen(archivo_url)
        descargafile = open(archivo_path, 'w')
        descargafile.write(webfile.read())
        webfile.close()
        descargafile.close()

        im = Image.open(archivo_path)
        pngpath = '%s.png' % archivo_path
        im.save(pngpath)

        nombre_base = '%s-%s' % (datetime.now().strftime('%F'), clip.pk)
        nombre_imagen = 'imagen-%s.png' % nombre_base
        imagen_content = ContentFile(open(pngpath).read())

        clip.imagen.save(nombre_imagen, imagen_content, save=False)
        clip.transferido = False
        # clip.save()

        os.remove(archivo_path)
        os.remove(pngpath)

    clip.titulo = request.POST.get('titulo')
    clip.descripcion = request.POST.get('descripcion')
    clip.usuario_modificacion = request.POST.get('usuario_remoto')

    if request.POST.get('tipo'):
        clip.tipo = TipoClip.objects.get(slug=request.POST.get('tipo'))

    categoria = Categoria.objects.get(slug=request.POST.get('categoria')) if request.POST.get('categoria') else None
    clip.categoria = categoria

    programa = Programa.objects.get(slug=request.POST.get('programa')) if request.POST.get('programa') else None
    clip.programa = programa

    clip.seleccionado = request.POST.get('seleccionado') in ['1', 'true']

    clip.observaciones = u'%s\nEditado desde Admin por %s en %s' % (clip.observaciones or '', request.POST.get('usuario_remoto'), datetime.now().isoformat())
    # if request.POST.get('tags'):
    #     clip.tags = request.POST.get('tags')
    if request.POST.get('hashtags'):
        clip.hashtags = request.POST.get('hashtags')
    clip.corresponsal = Corresponsal.objects.filter(slug=request.POST.get('corresponsal'))[0] if request.POST.get('corresponsal') else None
    # if 'ciudad' in request.POST:
    #     clip.ciudad = request.POST.get('ciudad')
    if 'pais' in request.POST:
        pais = Pais.objects.get(codigo=request.POST.get('pais')) if request.POST.get('pais') else None
        clip.pais = pais
    if 'publicado' in request.POST:
        clip.publicado = request.POST.get('publicado') in ['1', 'true']
    if 'tema' in request.POST and request.POST.get('tema'):
        clip.tema = Tema.objects.get(slug=request.POST.get('tema'))
    clip.save()

    return HttpResponse('{"success": true}', content_type="application/json")


@csrf_exempt
def eliminar_clip(request):
    try:
        if request.POST.get('id'):
            obj = Clip.objects.get(pk=request.POST.get('id'))
        else:
            obj = Clip.objects.get(slug=request.POST.get('slug'))
    except Clip.DoesNotExist:
        raise Http404()

    obj.delete()

    return HttpResponse('{"success": true}', content_type="application/json")



@csrf_exempt
def despublicar_clip(request):
    if request.POST.get('id'):
        clip = Clip.objects.get(pk=request.POST.get('id'))
    else:
         clip = Clip.objects.get(slug=request.POST.get('slug'))
    clip.publicado = False
    clip.usuario_publicacion = None
    clip.fecha_publicacion = None
    clip.observaciones += u'\nDespublicado desde Admin por %s en %s' % (request.POST.get('usuario_remoto'), datetime.now().isoformat())
    clip.save()

    return HttpResponse('{"success": true}', content_type="application/json")


@csrf_exempt
def publicar_clip(request):
    if request.POST.get('id'):
        clip = Clip.objects.get(pk=request.POST.get('id'))
    else:
         clip = Clip.objects.get(slug=request.POST.get('slug'))
    clip.publicado = True
    clip.usuario_publicacion = request.POST.get('usuario_publicacion')
    clip.fecha_publicacion = datetime.now()
    clip.observaciones += u'\nPublicado desde Admin por %s en %s' % (request.POST.get('usuario_remoto'), datetime.now().isoformat())
    clip.save()

    return HttpResponse('{"success": true}', content_type="application/json")



def tail(f, n):
  stdin,stdout = os.popen2("tail -n %s %s" % (n, f))
  stdin.close()
  lines = stdout.readlines(); stdout.close()
  return ''.join(lines)
