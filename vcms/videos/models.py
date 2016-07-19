# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from datetime import datetime, timedelta
import os
import uuid

from autoslug import AutoSlugField
from cacheback.queryset import QuerySetGetJob, QuerySetFilterJob
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from jsonfield import JSONField
from locality.models import Country, Territory
from model_utils import Choices, FieldTracker
from model_utils.fields import StatusField, MonitorField
from mptt.models import MPTTModel, TreeForeignKey
import shortuuid
from sorl.thumbnail import ImageField as SorlImageField, delete as delete_thumbnail
from taggit.managers import TaggableManager


temporales_storage = FileSystemStorage(location=settings.TEMPORALES_ROOT)
originales_storage = FileSystemStorage(location=settings.ORIGINALES_ROOT)
media_storage = FileSystemStorage(location=settings.MEDIA_ROOT)


ESTADO_CHOICES = Choices(
    ('despublicado', _('Despublicado')),
    ('publicado', _('Publicado')),
)

ORIGEN_CHOICES = Choices(
    ('local', _('Subir archivo de video')),
    ('externo', _('Importar video publicado en Internet')),
)

PLATAFORMA_TIPO_CHOICES = Choices(
    ('web', _('Sitio web')),
    ('movil', _('Aplicación móvil')),
    ('tv', _('Aplicación para TV')),
    ('youtube', _('Canal de YouTuve')),
)

PROCESAMIENTO_CHOICES = Choices(
    ('nuevo', _('En cola')),
    ('procesando', _('Procesando')),
    ('listo', _('Listo')),
    ('error', _('Error')),
)

REPRODUCCION_CHOICES = Choices(
    ('auto', _('Automático')),
    ('local', _('Sólo desde el sitio web')),
    ('youtube', _('Sólo desde YouTube')),
)

OPERADOR_CHOICES = Choices(
    ('exact', _('Es igual a')),
    ('not_exact', _('Es diferente a')),
    ('not_null', _('No está vacío')),
    ('null', _('Está vacío')),
    ('icontains', _('Contiene el texto')),
    ('lt', _('Es menor que')),
    ('lte', _('Es menor o igual que')),
    ('gt', _('Es mayor que')),
    ('gte', _('Es mayor o igual que')),
)

LINK_TIPO_CHOICES = Choices(
    ('auto', _('Genérico')),
    ('site', _('Sitio web')),
    ('post', _('Artículo o post relacionado')),
    ('social', _('Cuenta o perfil de redes sociales')),
    ('mailto', _('Correo electrónico')),
)

MARGEN_CHOICES = (
    (None, _('Automático')),
    ('0',  _('Sin margen')),
    ('10', _('10%')),
    ('20', _('20%')),
    ('30', _('30%')),
)

PLANTILLA_CHOICES = (
    (None, _('Automático')),
    ('default', _('Cuadros')),
    ('invertido', _('Cuadros invertido')),
    ('carrusel', _('Carrusel')),
)

ACTIVO_CHOICES = (
    (None, _('Automático')),
    (True, _('Sí')),
    (False, _('No'))
)

MOSTRAR_MAXIMO_CHOICES = (
    (None, _('Automático')),
    (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'),
    (8, '8'), (9, '9'), (10, '10'), (12, '12'), (18, '18'), (24, '24'),
    (36, '36'), (48, '48')
)

LAYOUT_CHOICES = Choices(
    (None, _('Automático')),
    ('c100', '1'),
    ('c50', '2'),
    ('c33', '3'),
    ('c25', '4'),
)

class ModelBase(models.Model):
    """
    Base model with created_at/updated_at fields
    """
    fecha_creacion = models.DateTimeField(
        _('fecha de creación'), db_index=True, auto_now_add=True,
        editable=False)
    fecha_modificacion = models.DateTimeField(
        _('última modificación'), null=True, blank=True, auto_now=True,
        editable=False)
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL, blank=True, null=True,
        related_name='%(class)ss_creados', verbose_name=_('creado por'))
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL, blank=True, null=True,
        related_name='%(class)ss_modificados', verbose_name=_('modificado por'))

    class Meta:
        abstract = True
        ordering = ['-fecha_creacion', '-pk']
        get_latest_by = 'fecha_creacion'


class DisplayableMixin(models.Model):
    mostrar_nombre = models.NullBooleanField(
        _('mostrar nombre'), choices=ACTIVO_CHOICES, null=True)
    mostrar_maximo = models.PositiveSmallIntegerField(
        _('mostrar máximo'), choices=MOSTRAR_MAXIMO_CHOICES,
        default=0, null=True, blank=True)
    mostrar_descripcion = models.NullBooleanField(
        _('mostrar descripción'), choices=ACTIVO_CHOICES, null=True)
    mostrar_paginacion = models.NullBooleanField(
        _('mostrar paginacón'), choices=ACTIVO_CHOICES, null=True)
    texto_paginacion = models.CharField(
        _('texto de paginación'), max_length=64, blank=True,
        help_text=_('Ej: Mostrar más'))
    tema = models.CharField(
        _('tema'), max_length=64, null=True, blank=True,
        choices=PLANTILLA_CHOICES)
    margen = models.CharField(
        _('margen'), max_length=64, choices=MARGEN_CHOICES,
        default=MARGEN_CHOICES[0][0], blank=True, null=True)
    layout = models.CharField(
        _('layout'), choices=LAYOUT_CHOICES, max_length=64,
        null=True, blank=True)
    mostrar_publicidad = models.NullBooleanField(
        _('mostrar publicidad'), choices=ACTIVO_CHOICES, null=True, blank=True)
    css = models.TextField(_('CSS'), blank=True)

    def get_display_parent(self):
        if self._meta.model_name != Plataforma._meta.model_name:
            return Plataforma.objects.filter(tipo='web').latest('fecha_creacion')

    def get_display_attr(self, attr):
        if hasattr(self, attr):
            val = getattr(self, attr, None)
            blankable = ('nombre', 'descripcion', 'texto_paginacion')
            if any((val is None, not val and attr in blankable)):
                parent = self.get_display_parent()
                if parent:
                    val = parent.get_display_attr(attr)
            return val

    class Meta:
        abstract = True


class SortableMixin(models.Model):
    """Base sortable Model"""
    orden = models.PositiveIntegerField(_('orden'), db_index=True)

    class Meta:
        abstract = True
        ordering = ['orden', '-fecha_creacion', '-pk']


class ActivableMixin(models.Model):
    activo = models.BooleanField(_('activo'), default=True, db_index=True)

    class Meta:
        abstract = True


class NamedMixin(models.Model):
    """Model with name, description and slug"""
    slug = AutoSlugField(populate_from='nombre', always_update=True)
    nombre = models.CharField(_('nombre'), max_length=255, blank=True)
    descripcion = models.TextField(_('descripción'), blank=True)
    meta_descripcion = models.TextField(_('meta descripción'), blank=True)
    tags = TaggableManager(_('tags'), blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        abstract = True


class TitledMixin(models.Model):
    """Model with name, description and slug"""
    slug = AutoSlugField(populate_from='titulo', always_update=True)
    titulo = models.CharField(_('título'), max_length=255, blank=True)
    descripcion = models.TextField(_('descripción'), blank=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        abstract = True


class Filtro(models.Model):
    OPERADOR = OPERADOR_CHOICES

    pagina = models.ForeignKey('Pagina', verbose_name=_('pagina'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    operador = StatusField(
        choices_name='OPERADOR', default=OPERADOR.exact,
        verbose_name=_('operador'))


class ListaEnPagina(ModelBase, SortableMixin, DisplayableMixin):
    nombre = models.CharField(
        _('nombre'), max_length=255, blank=True,
        help_text=_('Opcional, si se deja vacío se usará el nombre de la lista'))
    descripcion = models.TextField(_('descripción'), blank=True)
    lista = models.ForeignKey(
        'Lista', related_name='listas_en_pagina', verbose_name=_('lista'))
    pagina =  models.ForeignKey(
        'Pagina', related_name='listas_en_pagina', verbose_name=_('página'))

    def get_display_parent(self):
        return self.pagina

    def slug(self):
        return self.lista.slug

    def videos_recientes(self):
        videos = self.lista.videos.publicos()
        if self.mostrar_maximo:
            return videos[:self.mostrar_maximo]
        return videos

    class Meta:
        ordering = ['orden']
        unique_together = (("lista", "pagina"),)
        verbose_name = _('lista en página')
        verbose_name_plural = _('liestas en página')


class VideoEnPagina(ModelBase, SortableMixin, DisplayableMixin):
    """ManyToMany relation's 'thtough' class between Video and Pagina"""
    video = models.ForeignKey(
        'Video', models.CASCADE,
        related_name='videos_en_pagina', verbose_name=_('video'))
    pagina = models.ForeignKey(
        'Pagina', models.CASCADE,
        related_name='videos_en_pagina', verbose_name=_('página'))

    def get_display_parent(self):
        return self.pagina

    def slug(self):
        return self.pagina.slug

    def get_clasificador(self, clasificador):
        return self.video.get_clasificador(clasificador)

    class Meta:
        ordering = ['orden']
        unique_together = (("video", "pagina"),)
        verbose_name = _('vdeo en página')
        verbose_name_plural = _('videos en página')


class Clasificador(ModelBase, NamedMixin):
    nombre_plural = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = _('clasificador')
        verbose_name_plural = _('clasificadores')


class Link(ModelBase):
    TIPO = LINK_TIPO_CHOICES

    url = models.URLField(_('URL'), db_index=True)
    titulo = models.CharField(_('título'), max_length=255, blank=True)
    blank = models.BooleanField(
        _('nuevo tab'), default=False,
        help_text=_('Abrir link en una nuevva ventana o pestaña'))
    tipo = StatusField(_('tipo'), choices_name='TIPO', default=TIPO.auto)

    def __unicode__(self):
        if self.titulo:
            return '{0} ({1})'.format(self.titulo, self.url)
        else:
            return self.url

    class Meta:
        verbose_name = _('link')
        verbose_name_plural = _('links')


class ListaQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de listas
    """
    def clasificacion(self, clasificador, slug=None):
        if not isinstance(clasificador, Clasificador):
            clasificador = Clasificador.objects.get(slug=clasificador)
        listas = self.filter(clasificador=clasificador).select_related('pagina')
        return slug and listas.get(slug=slug) or listas


class Lista(ModelBase, NamedMixin, ActivableMixin):
    REPRODUCCION = REPRODUCCION_CHOICES

    nombre_plural = models.CharField(
        max_length=255, blank=True, help_text=_((
            'Opcional. Para hacer referencia al grupo de videos '
            'que pertenecen a esta lissta. Únicamente cuando el nombre sea '
            'pluralizable. Ej: Documenal -> Documentales, pero no Ciencia '
            'Ficción -> Ciencias Ficciones)')))
    clasificador = models.ForeignKey('Clasificador', related_name='listas')
    pagina = models.OneToOneField(
        'Pagina', verbose_name=_('página'), related_name='lista_principal',
        help_text=_('Sólo si existe una página dedicada a esta lista'),
        null=True, blank=True)
    youtube_playlist = models.CharField(
        _('playlist de YouTube'), max_length=128, blank=True)
    links = models.ManyToManyField(
        'Link', related_name='%(class)ss', verbose_name=_('link'), blank=True)
    imagen = SorlImageField(
        _('imagen'), upload_to='series', blank=True, null=True)
    mostrar_imagen = models.BooleanField(default=False, help_text=u'')
    icono = SorlImageField(
        upload_to='icons', blank=True, null=True, verbose_name=_('ícono'))
    mostrar_icono = models.BooleanField(_('mostrar ícono'), default=False)
    cortinilla_inicial = models.FileField(
        _('cortinilla inicial'), upload_to='intros',
        blank=True, null=True)
    mostrar_cortinilla_inicial = models.BooleanField(
        _('mostrar cortinilla inicial'), default=False)
    cortinilla_final = models.FileField(
        _('cortinilla final'), upload_to='endings', blank=True, null=True)
    mostrar_cortinilla_final = models.BooleanField(
        _('mostrar cortinilla final'), default=False)
    reproduccion = StatusField(
        _('reproducción'), choices_name='REPRODUCCION',
        default=REPRODUCCION.auto)
    listas_relacionadas = models.ManyToManyField(
        'self', blank=True, verbose_name=_('listas relacionadas'))

    # Default Manager
    objects = ListaQuerySet.as_manager()

    def __unicode__(self):
        return _('%s: %s') % (self.clasificador, self.nombre)

    class Meta:
        ordering = ['clasificador', 'nombre', '-fecha_creacion']
        verbose_name = _('lista')
        verbose_name_plural = _('listas')


class Pagina(MPTTModel, SortableMixin, NamedMixin, ActivableMixin, DisplayableMixin):
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True,
        verbose_name=_('página padre'))
    mostrar_en_menu = models.BooleanField(
        _('mostrar en menú'), default=True, db_index=True)
    listas = models.ManyToManyField(
        'Lista', related_name='paginas', through='ListaEnPagina',
        verbose_name=_('listas'))
    videos = models.ManyToManyField(
        'Video', related_name='paginas', through='VideoEnPagina',
        verbose_name=_('videos destacados'))

    class MPTTMeta:
        order_insertion_by = ['orden']

    def get_absolute_url(self):
        if settings.FRONTEND_URL:
            return '%s/secciones/%s?nc=%s' % (settings.FRONTEND_URL, self.slug, uuid.uuid4())

    def save(self, *args, **kwargs):
        super(Pagina, self).save(*args, **kwargs)
        Pagina.objects.rebuild()  # required by Suit

    class Meta:
        verbose_name = _('página')
        verbose_name_plural = _('páginas')


class Plataforma(ModelBase, SortableMixin, NamedMixin, DisplayableMixin):
    TIPO = PLATAFORMA_TIPO_CHOICES

    tipo = StatusField(choices_name='TIPO', verbose_name=_('tipo'))
    api_key = models.CharField(max_length=32, blank=True, db_index=True)
    link = models.ForeignKey(
        'Link', models.SET_NULL, related_name='plataformas',
        verbose_name='link', blank=True, null=True)

    def __unicode__(self):
        return '[{0}] {1}'.format(str(self.tipo).upper(), self.nombre)

    def get_absolute_url(self):
        return self.link and self.link.url

    class Meta:
        ordering = ['pk']
        verbose_name = _('plataforma')
        verbose_name_plural = _('plataformas')


class VideoQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de videos
    """
    def publicos(self):
        return self.filter(
            procesamiento=Video.PROCESAMIENTO.listo,
            estado=Video.ESTADO.publicado,
            fecha__lte=datetime.now()
        ).select_related('territorio', 'pais').prefetch_related('listas')

    def clasificados(self, lista):
        if isinstance(lista, Lista):
            return self.filter(listas=lista)
        elif isinstance(lista, str):
            return self.filter(listas__slug=lista)


class Video(ModelBase, TitledMixin, DisplayableMixin):
    # PROVISIONAL
    custom_metadata = JSONField(null=True, blank=True)
    viejo_slug = models.CharField(max_length=255, blank=True, db_index=True)

    ESTADO = ESTADO_CHOICES
    PROCESAMIENTO = PROCESAMIENTO_CHOICES
    REPRODUCCION = REPRODUCCION_CHOICES
    ORIGEN = ORIGEN_CHOICES

    # Status
    estado = StatusField(
        choices_name='ESTADO', default=ESTADO.despublicado,
        verbose_name=_('estado'))
    procesamiento = StatusField(
        choices_name='PROCESAMIENTO', default=PROCESAMIENTO.nuevo,
        verbose_name=_('procesamiento'))
    reproduccion = StatusField(
        choices_name='REPRODUCCION', default=REPRODUCCION.auto,
        verbose_name=_('reproducción'))
    origen = StatusField(
        choices_name='ORIGEN', default=ORIGEN.local, verbose_name=_('origen'))

    # local
    origen_url = models.URLField(
        _('URL origen'), blank=True, null=True, help_text=_(
            ('Dirección URL del video a copiar, puede ser un archivo para '
             'descarga directa (MP4, MOV, AVI, etc) o bien un a página desde '
             'donde sea posible extraer un video (YouTube, Dailymotion, '
             'TeleSUR, entre otros)')))
    archivo_fuente = models.FileField(
        _('archivo fuente'), upload_to='videos', storage=originales_storage)
    archivo_original = models.CharField(
        _('original'), max_length=255, blank=True)
    imagen_original = models.CharField(
        _('imagen_original'), max_length=255, blank=True)

    # YouTube
    youtube_id = models.CharField(
        _('ID de Youtube'), max_length=32, blank=True, editable=False)

    # video
    archivo = models.FileField(
        _('archivo'), upload_to='videos', blank=True, null=True)
    imagen = SorlImageField(
        verbose_name=_('imagen'), upload_to='images', blank=True, null=True)
    captions = models.FileField(
        _('subtítulos'), upload_to='captions', blank=True, null=True)

    # derivated
    sprites = models.FileField(
        _('sprites'), upload_to='sprites', blank=True, null=True)
    hls = models.FileField(
        _('HLS'), upload_to='hls', blank=True, null=True, editable=False)
    dash = models.FileField(
        _('DASH'), upload_to='dash', blank=True, null=True, editable=False)
    webm = models.FileField(
        _('WebM'), upload_to='webm', blank=True, null=True, editable=False)
    max_resolucion = models.IntegerField(
        _('resolución máxima'), db_index=True, blank=True, null=True,
        editable=False)

    # stream info
    duracion = models.DurationField(_('duración'), null=True, blank=True)
    width = models.PositiveIntegerField(_('anchura'), null=True, blank=True)
    height = models.PositiveIntegerField(_('altura'), null=True, blank=True)
    resolucion = models.IntegerField(
        _('resolución'), db_index=True, blank=True, null=True, editable=False)
    original_metadata = JSONField(null=True, blank=True)
    fps = models.FloatField(
        _('FPS'), blank=True, null=True, default=0, editable=False)

    # editorial
    fecha = models.DateTimeField(
        _('fecha'), db_index=True, default=timezone.now)
    meta_descripcion = models.TextField(_('transcripción'), blank=True)
    observaciones = models.TextField(_('observaciones'), blank=True)

    # ManyToMany
    listas = models.ManyToManyField(
        'Lista', related_name='videos', blank=True, verbose_name=_('listas'))
    links = models.ManyToManyField(
        'Link', related_name='videos', blank=True, verbose_name=_('links'))
    tags = TaggableManager(_('tags'), blank=True)

    # Location
    ciudad = models.CharField(
        _('ciudad'), max_length=128, blank=True, null=True)
    #pais = CountryField(_('país'), blank_label=_('selecciona país'), blank=True)
    pais = models.ForeignKey(
        Country, verbose_name=_('país'), blank=True, null=True)
    territorio = models.ForeignKey(
        Territory, verbose_name=_('territorio'), blank=True, null=True)

    # Tracking
    fecha_publicacion = MonitorField(
        _('fecha de publicación'), monitor='estado', when=['publicado'])
    tracker = FieldTracker()

    # Default Manager
    objects = VideoQuerySet.as_manager()

    def __unicode__(self):
        if self.procesamiento == 'listo' and self.titulo:
            return self.titulo
        else:
            return '{0}: [{1}]'.format(
                self.pk, self.PROCESAMIENTO[self.procesamiento])

    def get_absolute_url(self):
        return reverse('video', kwargs={ 'video_slug': self.slug,
                                         'video_uuid': self.uuid })

    def get_admin_form_tabs(self):
        return GET_VIDEO_TABS(self)

    def get_clasificacion(self, clasificador):
        if self.listas:
            try:
                if not isinstance(clasificador, Clasificador):
                    clasificador = Clasificador.objects.get(slug=clasificador)
                clasificacion = self.listas.filter(clasificador=clasificador)
                if len(clasificacion) == 1:
                    return clasificacion[0]
                elif len(clasificacion) > 1:
                    return clasificacion
            except Clasificador.DoesNotExist:
                pass

    @property
    def video(self):
        return self

    @property
    def player(self):
        if settings.FRONTEND_URL:
            return '{0}/player/{1}/{2}'.format(
                settings.FRONTEND_URL, self.uuid, self.slug)
    
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
            return 'status/%s' % self.uuid

    @property
    def vstats_path(self):
        if self.uuid:
            return 'vstats/%s' % self.uuid

    @property
    def procesamiento_status(self):
        if self.procesamiento != self.PROCESAMIENTO.procesando:
            return

        from subprocess import check_output, CalledProcessError
        status = {'status': None}
        if temporales_storage.exists(self.status_path):
            with temporales_storage.open(self.status_path, 'r') as status_file:
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
                            status['seconds'] / status['total'], 2)
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

    @property
    def duracion_iso(self):
        return (datetime.min + (self.duracion or timedelta(0))).time() \
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
        verbose_name = _('video')
        verbose_name_plural = _('videos')
