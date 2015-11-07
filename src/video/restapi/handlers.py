# -*- coding: utf-8 -*-
from piston.handler import BaseHandler
from piston.utils import rc
from clips.models import *
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta
from django.conf import settings
from util import validar_request, clip_to_dict, paginar, filtrar_con_programa_relacionado, filtrar_con_clip_relacionado, filtrar_con_campo, filtrar_con_busqueda_texto
import re

PAISES_CACHE = {}

def get_clips():
    return Clip.objects.filter(publicado=True, transferido=True)


class ClipHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT')
    model = Clip
    medio = None

    # Juegos de campos
    fields_escenciales = ('slug', 'api_url', 'origen')
    fields_basicos = ('titulo', 'descripcion', 'fecha', 'duracion', 'seleccionado')
    fields_urls = ('archivo_video', 'navegador_url', 'player_url', 'player_url_publicidad', 'audio_url', 'archivo_url', 'descarga_url', 'thumbnail_grande', 'thumbnail_mediano', 'thumbnail_pequeno', 'metodo_preferido')
    #fields_detalles = ('vistas', 'id_youtube', 'id_vimeo')
    fields_detalles = ('vistas',)
    fields_relaciones = ('tipo', 'categoria')

    fields_desuso = ('url',)
    fields_antiguos = fields_desuso + ('slug', 'titulo', 'descripcion', 'fecha', 'duracion', 'geotag',
                                       'audio_url', 'archivo_url', 'thumbnail_grande', 'thumbnail_mediano', 'thumbnail_pequeno',
                                       'ciudad', 'hashtags', 'tipo', 'pais', 'personajes', 'categoria', 'programa', 'corresponsal', 'tema')

    fields = fields_escenciales + fields_basicos + fields_urls + fields_detalles + fields_relaciones + fields_desuso

    @classmethod
    def origen(cls, obj):
        return {
            'id': obj.origen,
            'descripcion': obj.get_origen_display()
        }

    @classmethod
    def vistas(cls, obj):
        return obj.vistas

    # @classmethod
    # def estadisticas(cls, obj):
    #     return {
    #         'popularidad': obj.indice_yt_viewcount,
    #         'yt_viewcount': obj.yt_viewcount,
    #         'fecha_yt_viewcount': obj.fecha_yt_viewcount,
    #         'indice_yt_viewcount': obj.indice_yt_viewcount
    #     }

    @classmethod
    def archivo_url(cls, obj):
        if cls.medio == 'radiosur':
            return obj.audio_url()
        else:
            return obj.archivo_url()

    @classmethod
    def id_youtube(cls, obj):
        return obj.ciudad

    # @classmethod
    # def id_vimeo(cls, obj):
    #     return obj.produccion

    @classmethod
    def api_url(cls, obj):
        if obj.slug:
            return '%s/api/v1/clip/%s/?detalle=completo' % (settings.HOST, obj.slug)

    @classmethod
    def archivo_video(cls, obj):
        if obj.ciudad:
            return None

        if obj.fps == 990:
            return [{ 'mimetype': 'video/mp4', 'url': obj.get_archivo_url() }, { 'mimetype': 'video/webm', 'url': obj.get_archivo_url().replace('.mp4', '.webm')}, { 'mimetype': 'video/ogg', 'url': obj.get_archivo_url().replace('.mp4', '.ogv')}]
        else:
            return [{ 'mimetype': 'video/mp4', 'url': obj.get_archivo_url() }]

    @classmethod
    def embed_tag_inline(cls, obj):
        return ''

    @classmethod
    def player_javascript_url(cls, obj):
        return ''

    @classmethod
    def player_url_publicidad(cls, obj):
        return ''

    @classmethod
    def player_url(cls, obj):
        if obj.origen == Clip.ORIGEN_PROPIO:
            return '%s/player/iframe/?slug=%s' % (settings.HOST, obj.slug)
        else:
            return 'http://www.youtube.com/embed/%s?' % obj.ciudad

    @classmethod
    def player_html_url(cls, obj):
        return ''#'http://widgets.openmultimedia.biz/player/widget.vtv.html?query_detalle=basico&query_slug=%s' % obj.slug

    @classmethod
    def descarga_url(cls, obj):
        if obj.ciudad:
            return None
        else:
            return '%s?descarga' % obj.get_archivo_url()

    @classmethod
    def streaming(cls, obj):
        identificador = obj.archivo.name.replace('clips/', '')
        return None
        return {
            'rtmp_server': 'rtmp://vod.openmultimedia.biz:1935/vod',
            'rtmp_file': 'mp4:%s' % identificador,
            'apple_hls_url': 'http://vod.openmultimedia.biz:1935/vod/mp4:%s/playlist.m3u8' % identificador,
            'rtsp_url': 'rtsp://vod.openmultimedia.biz:554/vod/mp4:%s' % identificador,
        }

    @classmethod
    def nitf_url(cls, obj):
        return obj.representacion_nitf_url()

    @classmethod
    def navegador_url(cls, obj):
        return getattr(obj, 'make_url')()

    @classmethod
    def metodo_preferido(cls, obj):
        if obj.duracion and obj.duracion.minute > 10:
            return 'http'
        else:
            return 'http'

    def create(self, request, slug=None):
        if slug is not None or 'slug' in request.POST or not 'archivo' in request.POST or not request.POST['archivo']:
            return rc.BAD_REQUEST

        if not validar_request(request.POST):
            return rc.FORBIDDEN

        actualizables = ['titulo', 'tipo', 'descripcion', 'publicado']
        clip = Clip()
        num=0
        for param, val in request.POST.items():
            if not param in actualizables: continue
            try:
                setattr(clip, param, val)
                num+=1
            except Exception, e:
                return { 'error': 'Imposible asignar el valor de "%s" a "%s' % (param, val) }
        return { 'success': 'true' }
        #clip.save()
        return clip

    def update(self, request, slug=None):
        if not slug and not request.PUT['slug']:
            return rc.NOT_FOUND

        if not validar_request(request.PUT):
            return rc.FORBIDDEN
        try:
            clip = Clip.objects.get(slug=slug or request.PUT['slug'])
        except Clip.DoesNotExist:
            return rc.NOT_FOUND

        actualizables = ['titulo', 'descripcion', 'publicado']

        num=0
        for param, val in request.PUT.items():
            if not param in actualizables: continue
            try:
                setattr(clip, param, val)
                num+=1
            except Exception, e:
                return { 'error': 'Imposible cambiar el valor de "%s" a "%s' % (param, val) }

        clip.save()

        return clip

    def read(self, request, slug=None, relacionados=None):

        if request.GET.get('detalle') == 'minimo':
            self.fields = self.fields_escenciales
        elif request.GET.get('detalle') == 'basico':
            self.fields = self.fields_escenciales + self.fields_basicos + self.fields_urls
        elif request.GET.get('detalle') == 'normal':
            self.fields = self.fields_escenciales + self.fields_basicos + self.fields_urls + self.fields_detalles
        elif request.GET.get('detalle') == 'completo':
            self.fields = self.fields_escenciales + self.fields_basicos + self.fields_urls + self.fields_detalles + self.fields_relaciones
        else:
            return rc.BAD_REQUEST
            #self.fields = self.fields_antiguos
            #self.fields = self.fields_escenciales + self.fields_basicos + self.fields_urls + self.fields_detalles + self.fields_relaciones + self.fields_desuso

        if 'HTTP_X_OMMEDIO' in request.META and request.META['HTTP_X_OMMEDIO'] == 'radiosur':
            ClipHandler.medio = 'radiosur'
            self.fields = [x for x in self.fields if x not in ('descarga_url', 'navegador_url', 'thumbnail_grande', 'thumbnail_mediano', 'thumbnail_pequeno', 'archivo_video')]
        else:
            ClipHandler.medio = 'vtv'

        if validar_request(request.GET) or request.GET.get('autenticado'):
            autenticado = True
            self.fields = self.fields + ('publicado', 'id')
        else:
            autenticado = False

        #if slug:
        if slug and not relacionados: # temporal para usar solo un hanlder para modelo Clip
            try:
                clips = Clip.objects.filter(slug=slug)
                clip = clips[0]
                if not clip.publicado:
                    return clip if autenticado else rc.NOT_FOUND
                else:
                    return clip
            except IndexError:
                if slug.isdigit() and autenticado:
                    try:
                        return Clip.objects.get(pk=slug)
                    except Clip.DoesNotExist:
                        return rc.NOT_FOUND
                return rc.NOT_FOUND

        elif autenticado and request.GET.get('id'):
            try:
                clip = Clip.objects.get(id=request.GET.get('id'))
                return clip
            except Clip.DoesNotExist:
                return rc.NOT_FOUND

        else:

            if autenticado:
                clips = Clip.objects.filter(transferido=True)
                if request.GET.get('publicado') in ('1', 'true'):
                    clips = clips.filter(publicado=True)
                elif request.GET.get('publicado') in ('0', 'false'):
                    clips = clips.filter(publicado=False)
            else:
                clips = Clip.objects.filter(transferido=True, publicado=True)
                #clips = get_clips()

            # Orden
            if request.GET.get('orden') in ('yt_viewcount', 'popularidad'):
                clips = clips.order_by('-indice_yt_viewcount', '-yt_viewcount')
            else:
                clips = clips.order_by('-fecha')

            # Tiempo
            desde, hasta = None, None

            if request.GET.get('desde'):
                desde = datetime.strptime(request.GET.get('desde'), "%Y-%m-%d")

            if request.GET.get('hasta'):
                hasta = datetime.strptime(request.GET.get('hasta') + ' 23:59:59', "%Y-%m-%d %H:%M:%S")

            tiempo = request.GET.get('tiempo')
            if tiempo == 'dia': dias = 1
            elif tiempo == 'semana': dias = 7
            elif tiempo == 'mes': dias = 30
            elif tiempo == 'ano': dias = 365
            else: dias = None

            if dias:
                td = timedelta(days=dias)
                if not desde and not hasta: desde = datetime.now() - td
                elif not desde: desde = hasta - td
                elif not hasta: hasta = desde + td

            if desde:
                clips = clips.filter(fecha__gte=desde)
            if hasta:
                clips = clips.filter(fecha__lte=hasta)

            ubicaciones = request.GET.getlist('region') or request.GET.getlist('ubicacion')
            if ubicaciones:
                ubicaciones_validas = []
                for u in ubicaciones:
                    ubicacion_sequence = filter(lambda x: u in (slugify(x[1]), 'excepto__%s' % slugify(x[1])), UBICACION_CHOICES)
                    try:
                        if re.match(r'^excepto__', u):
                            ubicaciones_validas.append('excepto__%s' % ubicacion_sequence[0][0])
                        else:
                            ubicaciones_validas.append(ubicacion_sequence[0][0])
                    except IndexError:
                        pass
                if ubicaciones_validas:
                    clips = filtrar_con_campo(clips, ubicaciones_validas, 'pais__ubicacion')
                else:
                    return rc.NOT_FOUND

            # filtros generales
            filtros = (('id', 'id'), ('slug', 'slug'), ('seleccionado', 'seleccionado'), ('tipo', 'tipo__slug'), ('categoria', 'categoria__slug'), ('pais', 'pais__slug'),
                      ('tema', 'tema__slug'), ('programa', 'programa__slug'),
                      ('geotag', 'geotag'), ('programa_tipo', 'programa__tipo__slug'),
                      ('corresponsal', 'corresponsal__slug',), ('usuario_creacion', 'usuario_creacion'),)
            for filtro in filtros: clips = filtrar_con_campo(clips, request.GET.getlist(filtro[0]), filtro[1])

            if request.GET.get('relacionados') or relacionados:
                slug_relacionados = slug or request.GET.get('relacionados', None)
                try:
                    clip = Clip.objects.get(slug=slug_relacionados)
                except Clip.DoesNotExist:
                    return []
                clips = clips.filter(pk__in=[x.pk for x in clip.get_relacionados(clips)])

            # if request.GET.getlist('tag'):
            #     try:
            #          tag = Tag.objects.get(name__in=request.GET.getlist('tag'))
            #          results = TaggedItem.objects.get_union_by_model(Clip, tag)
            #          clips = clips.filter(pk__in=[x.pk for x in results])
            #     except Exception, e:
            #         pass

            # búsqueda de texto
            clips = filtrar_con_busqueda_texto(clips, request.GET.get('texto'), ('titulo', 'descripcion'))

            # distincts
            distintos = request.GET.getlist('distinto')
            if distintos: clips = clips.order_by().order_by(*distintos).distinct(*distintos)

            # formato/estructura
            if request.GET.get('formato') in ('ext', 'json-gxt'):
                return {
                    'totalCount': clips.count(),
                    'clips': [clip_to_dict(clip, fields=self.fields_antiguos + ('fecha_semana',), exclude=self.exclude) for clip
                              in paginar(request, clips)]
                }
            else:
                return paginar(request, clips)


class CategoriaHanlder(BaseHandler):
    allowed_methods = ('GET',)
    exclude = ('_state', 'id')
    model = Categoria

    def read(self, request, slug=None):
        if slug:
            try:
                return Categoria.objects.get(slug=slug)
            except Categoria.DoesNotExist:
                return rc.NOT_FOUND
        else:
            categorias = Categoria.objects.all()
            categorias = filtrar_con_busqueda_texto(categorias, request.GET.get('texto'), ('nombre',))
            if request.GET.get('clip_tipo'):
                categorias = categorias.filter(clip__tipo__slug=request.GET.get('clip_tipo')) # filtrar_con_campo(categorias, request.GET.get('clip_tipo'), 'clip__tipo__slug')
            return paginar(request, filtrar_con_clip_relacionado(categorias))


class ProgramaHanlder(BaseHandler):
    allowed_methods = ('GET',)

    fields = ('slug', 'nombre', 'tipo', 'descripcion', 'imagen_url')
    model = Programa

    def read(self, request, slug=None):
        if slug:
            try:
                return Programa.objects.get(slug=slug)
            except Programa.DoesNotExist:
                return rc.NOT_FOUND
        else:
            programas = Programa.objects.filter(activo=True)

            programas = filtrar_con_campo(programas, request.GET.getlist('tipo'), 'tipo__slug')
            programas = filtrar_con_busqueda_texto(programas, request.GET.get('texto'), ('nombre',))

            return paginar(request, filtrar_con_clip_relacionado(programas))


class TipoProgramaHandler(BaseHandler):
    allowed_methods = ('GET',)
    exclude = ('_state', 'id')
    model = TipoPrograma

    def read(self, request, slug=None):
        if slug:
            try:
                return TipoPrograma.objects.get(slug=slug)
            except TipoPrograma.DoesNotExist:
                return rc.NOT_FOUND

        else:
            tipos = TipoPrograma.objects.all()

            return paginar(request, filtrar_con_programa_relacionado(tipos))


class TipoClipHandler(BaseHandler):
    allowed_methods = ('GET',)
    exclude = ('_state', 'id')
    model = TipoClip

    def read(self, request, slug=None):
        if slug:
            try:
                return TipoClip.objects.get(slug=slug)
            except TipoClip.DoesNotExist:
                return rc.NOT_FOUND

        else:
            tipos = TipoClip.objects.all()

            return paginar(request, filtrar_con_clip_relacionado(tipos))


class TemaHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('nombre', 'slug', 'fecha_creacion', 'fecha_caducidad',)
    exclude = ('_state', 'id')
    model = Tema

    def read(self, request, slug=None):
        if slug:
            try:
                return Tema.objects.get(slug=slug)
            except Tema.DoesNotExist:
                return rc.NOT_FOUND

        else:
            temas = Tema.objects.all()

            temas = filtrar_con_busqueda_texto(temas, request.GET.get('texto'), ('nombre',))

            return paginar(request, filtrar_con_clip_relacionado(temas))


class CorresponsalHandler(BaseHandler):
    allowed_methods = ('GET',)
    exclude = ('_state', 'id')
    model = Corresponsal

    def read(self, request, slug=None):
        if slug:
            try:
                return Corresponsal.objects.get(slug=slug)
            except Corresponsal.DoesNotExist:
                return rc.NOT_FOUND

        else:
            corresponsales = Corresponsal.objects.filter(activo=True)
            corresponsales = filtrar_con_campo(corresponsales, request.GET.getlist('twitter'), 'twitter')
            corresponsales = filtrar_con_busqueda_texto(corresponsales, request.GET.get('texto'), ('nombre',))

            return paginar(request, filtrar_con_clip_relacionado(corresponsales))


class PaisHandler(BaseHandler):
    allowed_methods = ('GET')
    exclude = ('_state', 'id')
    model = Pais

    class Callable:
        def __init__(self, anycallable):
            self.__call__ = anycallable

    def ubicacion(obj):
        return slugify(obj.get_ubicacion_display())

    ubicacion = Callable(ubicacion)

    def read(self, request, slug=None):
        if slug:
            if len(slug) == 2:
                try:
                    return Pais.objects.get(codigo=slug)
                except Pais.DoesNotExist:
                    return rc.NOT_FOUND
            else:
                ubicacion = filter(lambda x: slugify(x[1]) == slug, UBICACION_CHOICES)
                if ubicacion:
                    try:
                        paises = Pais.objects.filter(ubicacion=ubicacion[0][0])
                        return paginar(request, filtrar_con_clip_relacionado(paises))
                    except Pais.DoesNotExist:
                        return rc.NOT_FOUND
                else:
                    try:
                        return Pais.objects.get(slug=slug)
                    except Pais.DoesNotExist:
                        return rc.NOT_FOUND
        else:
            paises = Pais.objects.all()

            paises = filtrar_con_campo(paises, request.GET.getlist('geotag'), 'geotag')
            paises = filtrar_con_busqueda_texto(paises, request.GET.get('texto'), ('nombre',))

            ubicaciones = request.GET.getlist('ubicacion')
            if ubicaciones:
                ubicaciones_validas = []
                for u in ubicaciones:
                    ubicacion_sequence = filter(lambda x: slugify(x[1]) == u, UBICACION_CHOICES)
                    try:
                        ubicaciones_validas.append(ubicacion_sequence[0][0])
                    except IndexError:
                        pass
                if ubicaciones_validas:
                    paises = paises.filter(ubicacion__in=ubicaciones_validas)
                else:
                    return rc.NOT_FOUND

            return paginar(request, filtrar_con_clip_relacionado(paises))
