# -*- coding: utf-8 -*- #
from datetime import datetime, timedelta
import os
import uuid

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
#from django_countries.fields import CountryField
from jsonfield import JSONField
from locality.models import Country, Territory
from model_utils import Choices, FieldTracker
from model_utils.fields import StatusField, MonitorField
from mptt.models import MPTTModel, TreeForeignKey
from polymorphic.models import PolymorphicModel
import shortuuid
from sorl.thumbnail import ImageField as SorlImageField, delete as delete_thumbnail
from taggit.managers import TaggableManager

from mptt.models import MPTTModel, TreeForeignKey



ESTADO_CHOICES = Choices(
    ('despublicado', u'Despublicado'),
    ('publicado', u'Publicado'),
)

LISTA_LAYOUT_CHOICES = Choices(
    ('auto', u'Automático'),
    ('c100', u'1 columna'),
    ('c50', u'1 o 2 columnas'),
    ('c33', u'Hasta 3 columnas'),
    ('c25', u'Hasta 4 columnas'),
)

ORIGEN_CHOICES = Choices(
    ('local', u'Subir archivo de video'),
    ('externo', u'Importar video desde un sitio web'),
)

PLATAFORMA_TIPO_CHOICES = Choices(
    ('web', u'Sitio web'),
    ('movil', u'Aplicación móvil'),
    ('tv', u'Aplicación para TV'),
    ('youtube', u'Canal de YouTuve'),
)

PROCESAMIENTO_CHOICES = Choices(
    ('nuevo', u'En cola'),
    ('procesando', u'Procesando'),
    ('listo', u'Listo'),
    ('error', u'Error'),
)

REPRODUCCION_CHOICES = Choices(
    ('auto', u'Automático'),
    ('local', u'Sólo desde el sitio web'),
    ('youtube', u'Sólo desde YouTube'),
)

OPERADOR_CHOICES = Choices(
    ('igual', u'Es igual a'),
    ('diferente', u'Es diferente a'),
    ('notnull', u'No está vacío'),
    ('null', u'Está vacío'),
    ('contains', u'Contiene el texto'),
)

LINK_TIPO_CHOICES = Choices(
    ('auto', u'Genérico'),
    ('site', u'Home de sitio web'),
    ('post', u'Artículo o post con contenido relacionado'),
    ('social', u'Cuenta o perfil de redes sociales'),
    ('mailto', u'Cuenta de correo electrónico'),
)

NUM_VIDEOS_CHOICES = (
    (0, u'Automático'),
    (1, 'Hasta 1 video'),
    (2, 'Hasta 2 videos'),
    (3, 'Hasta 3 videos'),
    (4, 'Hasta 4 videos'),
    (5, 'Hasta 5 videos'),
    (6, 'Hasta 6 videos'),
    (8, 'Hasta 8 videos'),
    (9, 'Hasta 9 videos'),
    (10, 'Hasta 10 videos'),
    (12, 'Hasta 12 videos'),
    (12, 'Hasta 16 videos'),
    (18, 'Hasta 18 videos'),
    (24, 'Hasta 24 videos'),
    (36, 'Hasta 36 videos'),
    (48, 'Hasta 48 videos'),
)

class OverwriteStorage(FileSystemStorage):
    """FileSystem storage that overwrites existing files"""
    def get_available_name(self, name):
        if self.exists(name):
            img = File(open(os.path.join(self.location, name), 'w'))
            delete_thumbnail(img, delete_file=False)
            os.remove(os.path.join(self.location, name))
        return name


class ModelBase(models.Model):
    """Base model with created_at/updated_at fields"""
    fecha_creacion = models.DateTimeField(
        u'fecha de creación', db_index=True, auto_now_add=True, editable=False)
    fecha_modificacion = models.DateTimeField(
        u'última modificación', null=True, blank=True, auto_now=True,
        editable=False)
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name=u'creado por', related_name='%(class)ss_creados',
        blank=True, null=True)
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name=u'última modificación por', related_name='%(class)ss_modificados',
        blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-fecha_creacion', '-pk']
        get_latest_by = "fecha_creacion"


class SortableMixin(models.Model):
    """Base sortable Model"""
    orden = models.PositiveIntegerField(db_index=True)

    class Meta:
        abstract = True
        ordering = ['orden', '-fecha_creacion', '-pk']


class ActivableMixin(models.Model):
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class NamedMixin(models.Model):
    """Model with name, description and slug"""
    slug = AutoSlugField(populate_from='nombre', always_update=True)
    nombre = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(u'descripción', blank=True)

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        abstract = True


class TitledMixin(models.Model):
    """Model with name, description and slug"""
    slug = AutoSlugField(populate_from='titulo', always_update=True)
    titulo = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(u'descripción', blank=True)

    def __unicode__(self):
        return u'%s' % self.titulo

    class Meta:
        abstract = True


class Filtro(models.Model):
    pagina = models.ForeignKey('Pagina')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    OPERADOR = OPERADOR_CHOICES
    operador = StatusField(
        choices_name='OPERADOR', default=OPERADOR.igual, help_text=u'')


class ListaEnPagina(ModelBase, SortableMixin):
    nombre = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(u'descripción', blank=True)
    lista = models.ForeignKey('Lista', related_name='listas_en_pagina')
    pagina =  models.ForeignKey('Pagina', related_name='listas_en_pagina')
    mostrar_nombre = models.BooleanField(default=True, verbose_name='nom.')
    mostrar_descripcion = models.BooleanField(u'desc.', default=False)
    mostrar_paginacion = models.BooleanField(u'pág.', default=True)
    NUM_VIDEOS = NUM_VIDEOS_CHOICES
    num_videos = models.PositiveIntegerField(
        u'núm. de videos', choices=NUM_VIDEOS, default=0)
    LAYOUT = LISTA_LAYOUT_CHOICES
    layout = StatusField(
        choices_name='LAYOUT', default=LAYOUT.auto, help_text=u'')
    invertido = models.BooleanField(default=False)
    junto = models.BooleanField(default=False)

    def videos_recientes(self):
        videos = self.lista.videos.all()
        if self.num_videos:
            return videos[:self.num_videos]
        return videos

    class Meta:
        ordering = ['orden']
        unique_together = (("lista", "pagina"),)


class VideoEnPagina(ModelBase, SortableMixin):
    """ManyToMany relation's 'thtough' class between Video and Pagina"""
    video = models.ForeignKey(
        'Video', models.CASCADE, related_name='videos_en_pagina')
    pagina = models.ForeignKey(
        'Pagina', models.CASCADE, verbose_name=u'página',
        related_name='videos_en_pagina')
    invertido = models.BooleanField(default=False)

    class Meta:
        ordering = ['orden']
        verbose_name = u'vdeo en página'
        verbose_name_plural = u'videos en página'
        unique_together = (("video", "pagina"),)


class Pagina(MPTTModel, SortableMixin, TitledMixin, ActivableMixin):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            verbose_name=u'padre')
    mostrar_en_menu = models.BooleanField(default=False, db_index=True)
    mostrar_titulo = models.BooleanField(default=True)
    mostrar_descripcion = models.BooleanField(default=True)
    listas = models.ManyToManyField(u'Lista', related_name='paginas', through='ListaEnPagina')
    videos = models.ManyToManyField(u'Video', related_name='paginas', through='VideoEnPagina')
    invertido = models.BooleanField(default=False)
    junto = models.BooleanField(default=False)

    def get_absolute_url(self):
        return 'http://videos-stg.jornada.com.mx/secciones/%s?nc=%s' % (self.slug, uuid.uuid4())

    class MPTTMeta:
        order_insertion_by = ['orden']

    # It is required to rebuild tree after save, when using order for mptt-tree
    def save(self, *args, **kwargs):
        super(Pagina, self).save(*args, **kwargs)
        Pagina.objects.rebuild()

    class Meta:
        verbose_name = u'página'
        verbose_name_plural = u'páginas'



class Clasificador(ModelBase, NamedMixin):
    nombre_plural = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = u'clasificadores'


class VideoClasificado(models.Model):
    video = models.ForeignKey('Video')
    clasificador = models.ForeignKey('Clasificador')


class ListaQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de listas
    """
    def clasificacion(self, clasificador, slug=None):
        if not isinstance(clasificador, Clasificador):
            clasificador = Clasificador.objects.get(slug=clasificador)

        listas = self.filter(clasificador=clasificador).select_related('pagina')
        if slug:
            return listas.get(slug=slug)
        else:
            return listas

class Lista(ModelBase, NamedMixin, ActivableMixin):
    """Base class for playlist-like models"""
    nombre_plural = models.CharField(max_length=255, blank=True)
    clasificador = models.ForeignKey('Clasificador', related_name='listas')
    pagina = models.OneToOneField(
        'Pagina', related_name='lista_principal', null=True, blank=True,
        help_text=u'Página dedicada a mostrar contenido sobre esta lista')
    youtube_playlist = models.CharField(max_length=128, blank=True)
    tags = TaggableManager(u'tags', blank=True)
    links = models.ManyToManyField(
        'Link', blank=True, related_name='%(class)ss')
    imagen = SorlImageField(
        upload_to='series', blank=True, null=True, storage=OverwriteStorage())
    mostrar_imagen = models.BooleanField(default=False, help_text=u'')
    icono = SorlImageField(
        upload_to='icons', blank=True, null=True, verbose_name=u'ícono',
        storage=OverwriteStorage())
    mostrar_icono = models.BooleanField(default=False, help_text=u'')
    cortinilla_inicio = models.FileField(
        upload_to='intros', blank=True, null=True,
        help_text=u'Video introductorio o cortinilla de inicio')
    mostrar_cortinilla_inicio = models.BooleanField(
        default=False,
        help_text=u'Video con cortinilla de inicio')
    cortinilla_final = models.FileField(
        upload_to='endings', blank=True, null=True,
        help_text=u'video con cortinilla de cierre')
    mostrar_cortinilla_final = models.BooleanField(
        default=False,
        help_text=u'Agrgear cortinilla final a los videos de este autor')
    REPRODUCCION = REPRODUCCION_CHOICES
    reproduccion = StatusField(
        u'reproducción', choices_name='REPRODUCCION',
        default=REPRODUCCION.auto)
    listas_relacionadas = models.ManyToManyField('self', blank=True)

    # Default Manager
    objects = ListaQuerySet.as_manager()

    def __unicode__(self):
        return u'%s: %s' % (self.clasificador, self.nombre)

    class Meta:
        ordering = ['clasificador', 'nombre', '-fecha_creacion']




class Autor(Lista):
    class Meta:
        verbose_name_plural = u'autores'


class Plataforma(ModelBase, SortableMixin, NamedMixin):
    TIPO = PLATAFORMA_TIPO_CHOICES
    tipo = StatusField(choices_name='TIPO')
    api_key = models.CharField(max_length=32, blank=True, db_index=True)
    usar_publicidad = models.BooleanField(default=True, db_index=True)

    def __unicode__(self):
        return u'[%s] %s' % (str(self.tipo).upper(), self.nombre)

    class Meta:
        ordering = ['pk']



class Link(ModelBase):
    url = models.URLField(u'URL', db_index=True)
    titulo = models.CharField(u'título', max_length=255, blank=True)
    blank = models.BooleanField(u'nuevo tab', default=False,
                                help_text=u'Abrir en una nuevva ventana/tab')
    TIPO = LINK_TIPO_CHOICES
    tipo = StatusField(choices_name='TIPO', default=TIPO.auto)

    def __unicode__(self):
        if self.titulo:
            return u'%s (%s)' % (self.titulo, self.url)
        else:
            return u'%s' % self.url




class VideoQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de videos
    """
    def publicos(self):
        return self.filter(
                #procesamiento=Video.PROCESAMIENTO.listo,
                #estado=Video.ESTADO.publicado,
                fecha__lte=datetime.now()) \
            .select_related('territorio', 'pais').prefetch_related('listas')


class Video(ModelBase, TitledMixin):
    # Estado
    ESTADO = ESTADO_CHOICES
    estado = StatusField(choices_name='ESTADO',
                         default=ESTADO.despublicado)
    # Procesamiento
    PROCESAMIENTO = PROCESAMIENTO_CHOICES
    procesamiento = StatusField(choices_name='PROCESAMIENTO',
                                default=PROCESAMIENTO.nuevo)
    # Políticas de reproducción
    REPRODUCCION = REPRODUCCION_CHOICES
    reproduccion = StatusField(choices_name='REPRODUCCION',
                               default=REPRODUCCION.auto,
                               verbose_name=u'reproducción')
    # Origen
    ORIGEN = ORIGEN_CHOICES
    origen = StatusField(choices_name='ORIGEN', default=ORIGEN.local)

    # local
    origen_url = models.URLField(u'URL origen',
        blank=True, null=True, help_text=(
            u'Dirección URL del video a copiar, puede ser un archivo para '
            u'descarga directa (MP4, MOV, AVI, etc) o bien un a página desde '
            u'donde sea posible extraer un video (YouTube, Dailymotion, '
            u'TeleSUR, entre otros)')
        )
    archivo_original = models.CharField(u'archivo', max_length=255, blank=True)
    imagen_original = models.CharField(blank=True, max_length=255)

    # YouTube
    youtube_id = models.CharField(u'ID de Youtube',
        max_length=32, blank=True, editable=False
        )
    # video
    archivo = models.FileField(upload_to='videos', blank=True, null=True, storage=OverwriteStorage())
    imagen = SorlImageField(upload_to='images', blank=True, null=True, storage=OverwriteStorage())
    hls = models.FileField(u'HLS', upload_to='hls', blank=True, null=True, storage=OverwriteStorage())
    resolucion = models.IntegerField(u'resolución',
        db_index=True, blank=True, null=True
        )
    max_resolucion = models.IntegerField(u'resolución máxima',
        db_index=True, blank=True, null=True
        )
    dash = models.FileField(u'DASH', upload_to='dash', blank=True, null=True, storage=OverwriteStorage())
    sprites = models.FileField(upload_to='sprites', blank=True, null=True, storage=OverwriteStorage())
    captions = models.FileField(upload_to='captions', blank=True, null=True, storage=OverwriteStorage())

    # stream info
    duracion = models.DurationField(u'duración', default=timedelta(0))
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)
    original_metadata = JSONField(null=True, blank=True)
    fps = models.FloatField(blank=True, null=True, default=0, editable=False)

    # editorial
    fecha = models.DateTimeField(db_index=True, default=timezone.now)
    resumen = models.TextField(blank=True)
    transcripcion = models.TextField(u'transcripción', blank=True)
    observaciones = models.TextField(blank=True)

    # ManyToMany
    listas = models.ManyToManyField('Lista', related_name='videos', blank=True)
    links = models.ManyToManyField('Link', blank=True, related_name='videos')
    tags = TaggableManager(u'tags', blank=True,
        help_text=u'Palabras o frases clave separadas por coma')

    # Location
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    #pais = CountryField(u'país', blank_label=u'selecciona país', blank=True)
    pais = models.ForeignKey(Country, verbose_name=u'país', blank=True, null=True)
    territorio = models.ForeignKey(
        Territory, verbose_name=u'territorio', blank=True, null=True)

    # Tracking
    fecha_publicacion = MonitorField(
        u'fecha de publicación', monitor='estado', when=['publicado'])
    tracker = FieldTracker()

    # Default Manager
    objects = VideoQuerySet.as_manager()

    def __unicode__(self):
        if self.is_listo and self.titulo:
            return self.titulo
        else:
            return u'{0}: [{1}]'.format(
                self.pk, self.PROCESAMIENTO[self.procesamiento])

    def get_absolute_url(self):
        return reverse('video', kwargs={'video_slug': self.slug,
                                        'video_uuid': self.uuid })

    def get_admin_form_tabs(self):
        return GET_VIDEO_TABS(self)

    '''
    Properties
    '''
    @property
    def uuid(self):
        """
        string con ID aumentado a 8 caracteres, siempre de longitud LENGTH
        """
        LENGTH = 8
        if self.pk:
            str_pk = str(self.pk)
            long_uuid = shortuuid.ShortUUID(alphabet="123456789").uuid(str_pk)
            return "{0}0{1}".format(long_uuid[:LENGTH-1-len(str_pk)], str_pk)

    @property
    def status_path(self):
        if self.uuid:
            return os.path.join(settings.TEMP_ROOT, 'status', self.uuid)

    @property
    def vstats_path(self):
        if self.uuid:
            return os.path.join(settings.TEMP_ROOT, 'vstats', self.uuid)

    @property
    def procesamiento_status(self):
        from subprocess import check_output, CalledProcessError

        status = { 'status': None }

        if os.path.exists(self.status_path):
            with open(self.status_path, 'r') as status_file:
                status_list = status_file.read().split()

            if status_list:
                status['status'] = status_list[0]

                if status_list[0] == 'download':  # download has begun
                    status['progress'] = float(status_list[1])
                elif status_list[0] == 'valid':
                     # download has finished and compreession started
                    status['total'] = float(status_list[1])
                    try:
                        tailcmd = ['tail', '-2', self.vstats_path]
                        vstats_line = check_output(tailcmd).split("\n")[0]
                        status['seconds'] = float(vstats_line.split()[9])
                        status['progress'] = 100 * round(
                            status['seconds'] / status['total'], 2
                            )
                    except (CalledProcessError, IndexError):
                        # No vstats file or invalid
                        status['seconds'] = 0
                        status['progress'] = 0
                elif status_list[0] == 'done':
                    status['id'] = int(status_list[1])
                elif status_list[0] == 'error':
                    status['code'] = int(status_list[1])
                    status['msg'] = ' '.join(status_list[2:])
        return status

    # @procesamiento_status.setter
    # def procesamiento_status(self, status):
    #     valid_statuses = {
    #         'download': {'progress': float}
    #         'valid': {'total': float}
    #     }
    #     if status.get('status') in ['download', 'valid', 'done', 'error']:



    @property
    def descripcion_plain(self):
        return strip_tags(self.descripcion)

    @property
    def url(self):
        return self.get_absolute_url()

    '''
    Status
    '''
    @property
    def is_nuevo(self):
        return self.procesamiento == Video.PROCESAMIENTO.nuevo
    @property
    def is_procesando(self):
        return self.procesamiento == Video.PROCESAMIENTO.procesando
    @property
    def is_listo(self):
        return self.procesamiento == Video.PROCESAMIENTO.listo
    @property
    def is_error(self):
        return self.procesamiento == Video.PROCESAMIENTO.error

    '''
    Duration
    '''
    @property
    def duracion_iso(self):
        return (datetime.min + self.duracion).time() \
               .replace(microsecond=0).isoformat()
    @property
    def horas(self):
        return self.segundos//3600
    @property
    def minutos(self):
        return self.horas%60
    @property
    def segundos(self):
        return self.duracion.seconds

    class Meta:
        ordering = ('-fecha', '-fecha_creacion', '-pk')
