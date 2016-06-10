# -*- coding: utf-8 -*- #
import json
import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, mixins
from django.views.generic.base import RedirectView

from videos.models import *
from .serializers import *



class VideoRedirectView(RedirectView):
    def get_redirect_url(*args, **kwargs):
        return '%svideo/%s/%s/' % (
            settings.BASE_FRONTEND_URL, kwargs['video_uuid'],
            kwargs['video_slug'],
            )

'''
API
'''
class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class TipoViewSet(viewsets.ModelViewSet):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

class ListaViewSet(viewsets.ModelViewSet):
    queryset = Lista.objects.all()
    serializer_class = ListaSerializer

class SitioViewSet(viewsets.ModelViewSet):
    queryset = Sitio.objects.all()
    serializer_class = SitioSerializer




def crossdomain(request, **kwargs):
    return render(request, 'crossdomain.xml', {},
                  content_type='application/xml')


def cambiar_thumbnail(video):
    offset = video.duracion.seconds * random.random()
    cmd_imagen = 'ffmpeg -y -ss %d -i %s -vcodec png -vframes 1 -an -f rawvideo %s' % (offset, video.archivo.path, temp_path)
    call(cmd_imagen, shell=True)

    #video.save()
    video.save(update_fields=('imagen',))
    Video.objects.filter(pk=video.pk).update()

    return true


@csrf_exempt
def cambiar_thumbnail_view(request):
    video = get_object_or_404(Video, pk=request.POST.get('id'))
    result = cambiar_thumbnail(video)
    return HttpResponse(json.dumps(result), content_type="application/json")
   



# @csrf_exempt
# def crear_nuevo(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest('Invalid request')

#     uid = str(uuid.uuid4())
#     status_path = '%stemp/status/%s.txt' % (settings.STORAGE_DIR, uid)
#     with open(status_path, 'w') as status_file:
#         status_file.write('queue')
#     crear_nuevo_video_job.delay(request.POST, uid)

#     return HttpResponse(json.dumps({'success': True, 'uid': uid}), content_type="application/json")


@csrf_exempt
def query_nuevo_view(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    return HttpResponse(json.dumps(video.query_procesamiento),
                        content_type="application/json")

# @csrf_exempt
# def editar_video(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest('Invalid request')

#     if request.POST.get('id'):
#         video = Video.objects.get(pk=request.POST.get('id'))
#     else:
#          video = Video.objects.get(slug=request.POST.get('slug'), idioma_original=request.POST.get('idioma', 'es'))

#     if request.POST.get('archivo_img_id'):
#         archivo_url = 'http://upload.openmultimedia.biz/files/%s' % request.POST.get('archivo_img_id')
#         archivo_path = '/tmp/%s' % request.POST.get('archivo_img_id')
#         webfile = urllib2.urlopen(archivo_url)
#         descargafile = open(archivo_path, 'w')
#         descargafile.write(webfile.read())
#         webfile.close()
#         descargafile.close()

#         im = Image.open(archivo_path)
#         pngpath = '%s.png' % archivo_path
#         im.save(pngpath)

#         nombre_base = '%s-%s' % (datetime.now().strftime('%F'), video.pk)
#         nombre_imagen = 'imagen-%s.png' % nombre_base
#         imagen_content = ContentFile(open(pngpath).read())

#         video.imagen.save(nombre_imagen, imagen_content, save=False)
#         video.procesado = False
#         # video.save()

#         os.remove(archivo_path)
#         os.remove(pngpath)

#     video.titulo = request.POST.get('titulo')
#     video.descripcion = request.POST.get('descripcion')
#     video.hashtags = request.POST.get('hashtags')
#     video.seleccionado = request.POST.get('seleccionado') in ['1', 'true']
#     video.publicado = request.POST.get('publicado') in ['1', 'true']
#     video.tipo = Tipo.objects.get(slug=request.POST.get('tipo'))
#     video.categoria = Categoria.objects.get(slug=request.POST.get('categoria')) if request.POST.get('categoria') else None
#     video.programa = Programa.objects.get(slug=request.POST.get('programa')) if request.POST.get('programa') else None
#     video.corresponsal = Corresponsal.objects.filter(slug=request.POST.get('corresponsal'))[0] if request.POST.get('corresponsal') else None
#     video.tema = Tema.objects.get(slug=request.POST.get('tema')) if request.POST.get('tema') else None
#     video.pais = Pais.objects.get(codigo=request.POST.get('pais')) if request.POST.get('pais') else None

#     video.observaciones = u'%s\nEditado desde Admin por %s en %s' % (video.observaciones or '', request.POST.get('usuario_remoto'), datetime.now().isoformat())
#     video.usuario_modificacion = request.POST.get('usuario_remoto')

#     video.save()

#     return HttpResponse('{"success": true}', content_type="application/json")


# @csrf_exempt
# def eliminar_video(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest('Invalid request')

#     try:
#         if request.POST.get('id'):
#             obj = Video.objects.get(pk=request.POST.get('id'))
#         else:
#             obj = Video.objects.get(slug=request.POST.get('slug'))
#     except Video.DoesNotExist:
#         raise Http404()

#     obj.delete()

#     return HttpResponse('{"success": true}', content_type="application/json")



# @csrf_exempt
# def despublicar_video(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest('Invalid request')

#     if request.POST.get('id'):
#         video = Video.objects.get(pk=request.POST.get('id'))
#     else:
#          video = Video.objects.get(slug=request.POST.get('slug'))
#     video.publicado = False
#     video.usuario_publicacion = None
#     video.fecha_publicacion = None
#     video.observaciones += u'\nDespublicado desde Admin por %s en %s' % (request.POST.get('usuario_remoto'), datetime.now().isoformat())
#     video.save()

#     return HttpResponse('{"success": true}', content_type="application/json")


# @csrf_exempt
# def publicar_video(request):
#     if request.method != 'POST':
#         return HttpResponseBadRequest('Invalid request')

#     if request.POST.get('id'):
#         video = Video.objects.get(pk=request.POST.get('id'))
#     else:
#          video = Video.objects.get(slug=request.POST.get('slug'))
#     video.publicado = True
#     video.usuario_publicacion = request.POST.get('usuario_publicacion')
#     video.fecha_publicacion = datetime.now()
#     video.observaciones += u'\nPublicado desde Admin por %s en %s' % (request.POST.get('usuario_remoto'), datetime.now().isoformat())
#     video.save()

#     return HttpResponse('{"success": true}', content_type="application/json")



# def tail(f, n):
#   stdin,stdout = os.popen2("tail -n %s %s" % (n, f))
#   stdin.close()
#   lines = stdout.readlines(); stdout.close()
#   return ''.join(lines)
