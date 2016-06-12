import json
import os
import shutil

from isodate import parse_time

from videos.models import *
from vcms.video_ops import get_video_stream_info

SRC_ROOT = '/root/videos/tvstorage/'
DST_ROOT = '/mnt/vcms_storage/media/'


def new_descripcion(clip):
    return clip['descripcion']

TIPO_NOTICIA = Tipo.objects.get(nombre=u'Noticia')
TIPO_ENTREVISTA = Tipo.objects.get(nombre=u'Entrevista')
TIPO_REPORTAJE = Tipo.objects.get(nombre=u'Reportaje')
TIPO_VIDEOBLOG = Tipo.objects.get(nombre=u'Videoblog')
TIPO_CLIMA = Tipo.objects.get(nombre=u'Pronóstico del tiempo')
TIPO_VIDEOCHAT = Tipo.objects.get(nombre=u'Videochat')
TIPOS_DIRECTOS = {
    1: TIPO_NOTICIA, 2: TIPO_ENTREVISTA, 3: TIPO_REPORTAJE
}
def new_tipo(clip):
    if clip['categoria'] == 16:
        return TIPO_VIDEOBLOG
    elif clip['categoria'] == 14:
        return TIPO_VIDEOCHAT
    elif 'tico del tiempo' in clip['titulo'].lower() or 'tico del clima' in clip['titulo'].lower():
       return TIPO_CLIMA
    else:
        if clip['tipo'] in TIPOS_DIRECTOS:
            return TIPOS_DIRECTOS[clip['tipo']]
        else:
            return TIPO_NOTICIA

AUTOR_LAJORNADA = Autor.objects.get(nombre='La Jornada')
AUTOR_AP = Autor.objects.get(nombre='Associated Press (AP)')
AUTOR_CONAGUA = Autor.objects.get(nombre='CONAGUA')
def new_autor(clip):
    if clip['tipo'] == 4:
        return AUTOR_AP
    elif new_tipo(clip) == TIPO_CLIMA:
        return AUTOR_LAJORNADA

def new_duracion(clip):
    t = parse_time(clip['duracion'])
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


CATEGORIAS_DIRECTAS = {
    1: Categoria.objects.get(nombre=u'Política'),
    2: Categoria.objects.get(nombre=u'Opinión'),
    3: Categoria.objects.get(nombre=u'Economía'),
    4: Categoria.objects.get(nombre=u'Mundo'),
    5: Categoria.objects.get(nombre=u'Capital'),
    6: Categoria.objects.get(nombre=u'Sociedad'),
    7: Categoria.objects.get(nombre=u'Estados'),
    8: Categoria.objects.get(nombre=u'Ciencias'),
    9: Categoria.objects.get(nombre=u'Cultura'),
    10: Categoria.objects.get(nombre=u'Espectáculos'),
    11: Categoria.objects.get(nombre=u'Deportes'),
}
def new_categoria(clip):
    if clip['categoria'] in CATEGORIAS_DIRECTAS:
        return CATEGORIAS_DIRECTAS[clip['categoria']]
    else:
        return CATEGORIAS_DIRECTAS[1]

SITIO_LAJORNADA = Sitio.objects.get(nombre='La Jornada Videos')
def new_sitio(clip):
    return SITIO_LAJORNADA

def migrar(vmax=None):
    with open('jsondump', 'r') as f:
        dump = json.loads(f.read())
    youtube_clips = []
    file_mapping = []
    num = 0
    for obj in dump:
        if obj['model'] == 'clips.clip':
            num = num+1
            if vmax and num>vmax: break
            clip = obj['fields']
            if clip['ciudad']:
                # de YT,  guardar
                youtube_clips.append(obj)
            else:
                ## CLIP PROPIO
                video = Video(
                    titulo=clip['titulo'],
                    descripcion=new_descripcion(clip),
                    duracion = new_duracion(clip),
                    fecha = clip['fecha'],
                    tipo = new_tipo(clip),
                    autor = new_autor(clip),
                    categoria = new_categoria(clip),
                    observaciones = json.dumps(obj),
                    procesamiento='listo'
                )
                video.save()
                video.sitios.add(new_sitio(clip))
                video.tags = clip['tags']
                video.save()
                # copiar video
                new_archivo = 'videos/%s.mp4' % video.uuid
                shutil.move(os.path.join(SRC_ROOT, clip['archivo']), 
                            os.path.join(DST_ROOT, new_archivo))
                file_mapping.append((os.path.join(SRC_ROOT, clip['archivo']), 
                                    os.path.join(DST_ROOT, new_archivo)))
                #copiar imagen
                new_imagen = 'images/%s.jpg' % video.uuid
                shutil.move(os.path.join(SRC_ROOT, clip['imagen']),
                            os.path.join(DST_ROOT, new_imagen))
                file_mapping.append((os.path.join(SRC_ROOT, clip['imagen']),
                                     os.path.join(DST_ROOT, new_imagen)))
                vi = get_video_stream_info(os.path.join(DST_ROOT, new_imagen))
                Video.objects.filter(pk=video.pk).update(archivo=new_archivo,
                    imagen=new_imagen,
                    original_width=vi.get('width'),
                    original_height=vi.get('height'))
    with open('youtube.json', 'w') as f:
        f.write(json.dumps(youtube_clips))
    with open('files.json', 'w') as f:
        f.write(json.dumps(file_mapping))

def revert_files():
    with open('files.json', 'r') as f:
        files = json.loads(f.read())
    for pair in files:
        old, new = pair
        print('moviendo "%s" a "%s"' % (new, old))
        #shutil.move(new, old)