# -*- coding: utf-8 -*- #
import json
import os
import re
import shutil

from isodate import parse_time

from videos.models import *
from vcms.video_ops import get_video_stream_info

SRC_ROOT = '/root/videos/tvstorage/'
DST_ROOT = '/mnt/vcms_storage/media/'

MODIFY_FS = True
USE_EXISTING_OPTS = True
DELETE_ALL_FIRST = True
VIDEOS_MAX = -1
# state
found = {}

CIUDADES = [u'Ciudad de México', u'Estado de México']

def new_descripcion(clip):
    global found
    d = clip['descripcion'].strip()

    # strip date
    d = re.sub(r'\d{1,2}\s+de\s+.+\s+de\s+201\d\.*\s*', '', d).strip().strip(',')

    # city
    for ciudad in CIUDADES:
        ciudad_re = r'^\s*' + ciudad + r'[,\.]\s+(.+)$'
        m = re.match(ciudad_re, d, re.UNICODE)
        if m:
            print 'M encuentra'
            d = m.group(1)
            found['ciudad'] = ciudad

    found['descripcion'] = d
    return found.get('descripcion')

def new_ciudad(clip):
    global found
    return found.get('ciudad')

C_FORMATO = Clasificador.objects.get(slug='formato')
C_AUTOR = Clasificador.objects.get(slug='autor')
C_SECCION = Clasificador.objects.get(slug='seccion')
C_SERIE = Clasificador.objects.get(slug='serie')
C_TEMA = Clasificador.objects.get(slug='tema')

TIPO_NOTICIA = Lista.objects.get(clasificador=C_FORMATO, slug='noticia')
TIPO_ENTREVISTA = Lista.objects.get(clasificador=C_FORMATO, slug='entrevista')
TIPO_REPORTAJE = Lista.objects.get(clasificador=C_FORMATO, slug='reportaje')
TIPO_VIDEOBLOG = Lista.objects.get(clasificador=C_FORMATO, slug='videoblog')
TIPO_CLIMA = Lista.objects.get(clasificador=C_SERIE, slug='pronosticos-del-tiempo')
TIPO_VIDEOCHAT = Lista.objects.get(clasificador=C_FORMATO, slug='videochat')
TIPOS_DIRECTOS = {
    1: TIPO_NOTICIA, 2: TIPO_ENTREVISTA, 3: TIPO_REPORTAJE
}
def new_tipo(clip):
    if clip['categoria'] == 16:
        return TIPO_VIDEOBLOG
    elif clip['categoria'] == 14:
        return TIPO_VIDEOCHAT
    else:
        if clip['tipo'] in TIPOS_DIRECTOS:
            return TIPOS_DIRECTOS[clip['tipo']]
        else:
            return TIPO_NOTICIA

AUTOR_LAJORNADA = Lista.objects.get(clasificador=C_AUTOR, slug='la-jornada')
AUTOR_AP = Lista.objects.get(clasificador=C_AUTOR, slug='ap')
AUTOR_CONAGUA = Lista.objects.get(clasificador=C_AUTOR, slug='conagua')
def new_autor(clip):
    if clip['tipo'] == 4:
        return AUTOR_AP
    elif new_tipo(clip) == TIPO_CLIMA:
        return AUTOR_LAJORNADA

def new_duracion(clip):
    t = parse_time(clip['duracion'])
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


CATEGORIAS_DIRECTAS = {
    1: Lista.objects.get(clasificador=C_SECCION, slug='politica'),
    2: Lista.objects.get(clasificador=C_SECCION, slug='opinion'),
    3: Lista.objects.get(clasificador=C_SECCION, slug='economia'),
    4: Lista.objects.get(clasificador=C_SECCION, slug='mundo'),
    5: Lista.objects.get(clasificador=C_SECCION, slug='capital'),
    6: Lista.objects.get(clasificador=C_SECCION, slug='sociedad'),
    7: Lista.objects.get(clasificador=C_SECCION, slug='estados'),
    8: Lista.objects.get(clasificador=C_SECCION, slug='ciencias'),
    9: Lista.objects.get(clasificador=C_SECCION, slug='cultura'),
    10: Lista.objects.get(clasificador=C_SECCION, slug='espectaculos'),
    11: Lista.objects.get(clasificador=C_SECCION, slug='deportes'),
}
def new_categoria(clip):
    if clip['categoria'] in CATEGORIAS_DIRECTAS:
        return CATEGORIAS_DIRECTAS[clip['categoria']]
    else:
        return CATEGORIAS_DIRECTAS[1]


def new_serie(clip):
    if 'tico del tiempo' in clip['titulo'].lower() or 'tico del clima' in clip['titulo'].lower():
       return TIPO_CLIMA

def migrar():
    global found
    if DELETE_ALL_FIRST:
        Video.objects.all().delete()
    with open('jsondump', 'r') as f:
        dump = json.loads(f.read())
    youtube_clips = []
    file_mapping = []
    num = 0
    for obj in dump:
        if obj['model'] == 'clips.clip':
            num = num+1
            if VIDEOS_MAX > 0 and num>VIDEOS_MAX: break
            clip = obj['fields']
            if clip['ciudad']:
                # de YT,  guardar
                youtube_clips.append(obj)
            else:
                found = {}
                ## CLIP PROPIO
                video = Video(
                    titulo=clip['titulo'],
                    descripcion=new_descripcion(clip),
                    ciudad=new_ciudad(clip),
                    duracion = new_duracion(clip),
                    fecha = clip['fecha'],
                    observaciones = json.dumps(obj),
                    procesamiento='listo'
                )
                video.save()
                if new_tipo(clip):
                    video.listas.add(new_tipo(clip))
                if new_autor(clip):
                    video.listas.add(new_autor(clip))
                if new_categoria(clip):
                    video.listas.add(new_categoria(clip))
                if new_serie(clip):
                    video.listas.add(new_serie(clip))
                video.tags = clip['tags']
                video.save()
                # copiar video
                new_archivo = 'videos/%s.mp4' % video.uuid
                if MODIFY_FS:
                    try:
                        shutil.move(os.path.join(SRC_ROOT, clip['archivo']),
                                os.path.join(DST_ROOT, new_archivo)
                                )
                        file_mapping.append((os.path.join(SRC_ROOT, clip['archivo']),
                                os.path.join(DST_ROOT, new_archivo))
                                )
                    except IOError:
                        print "Error al copiar, borrando video"
                        video.delete()
                        continue
                #copiar imagen
                new_imagen = 'images/%s.jpg' % video.uuid
                if MODIFY_FS:
                    shutil.move(os.path.join(SRC_ROOT, clip['imagen']),
                                os.path.join(DST_ROOT, new_imagen))
                file_mapping.append((os.path.join(SRC_ROOT, clip['imagen']),
                                     os.path.join(DST_ROOT, new_imagen)))
                vi = get_video_stream_info(os.path.join(DST_ROOT, new_imagen))
                Video.objects.filter(pk=video.pk).update(archivo=new_archivo,
                    imagen=new_imagen,
                    original_width=vi.get('width'),
                    original_height=vi.get('height'))

                if USE_EXISTING_OPTS:
                    new_hls = 'hls/%s/playlist.m3u8' % video.uuid
                    if os.path.exists(os.path.join(DST_ROOT, new_hls)):
                        Video.objects.filter(pk=video.pk).update(hls=new_hls)

                    new_sprites = 'sprites/%s/s.vtt' % video.uuid
                    if os.path.exists(os.path.join(DST_ROOT, new_sprites)):
                        Video.objects.filter(pk=video.pk).update(
                            sprites=new_sprites)

    with open('outout-youtube.json', 'w') as f:
        f.write(json.dumps(youtube_clips))
    with open('output-files.json', 'w') as f:
        f.write(json.dumps(file_mapping))


def revert_files():
    with open('files.json', 'r') as f:
        files = json.loads(f.read())
    for pair in files:
        new, old = pair
        if not os.path.exists(new):
            print('moviendo "%s" a "%s"' % (old, new))
            shutil.move(old, new)
        else:
            print('ya existe "%s"' % new)
