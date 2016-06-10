# -*- coding: utf-8 -*- #
from datetime import datetime, timedelta
import os

from autoslug import AutoSlugField
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django_countries.fields import CountryField
from jsonfield import JSONField
from model_utils import Choices, FieldTracker
from model_utils.fields import StatusField, MonitorField
import shortuuid
from sorl.thumbnail import ImageField as SorlImageField
from taggit.managers import TaggableManager


REPRODUCCION_CHOICES = Choices(
    ('auto', u'Automático'),
    ('local', u'Sólo desde el sitio web'),
    ('youtube', u'Sólo desde YouTube'),
)

ESTADO_CHOICES = Choices(
    ('despublicado', u'Despublicado'),
    ('publicado', u'Publicado'),
)

PROCESAMIENTO_CHOICES = Choices(
    ('nuevo', u'En cola'),
    ('procesando', u'Procesando'),
    ('listo', u'Listo'),
    ('error', u'Error'),
)

ORIGEN_CHOICES = Choices(
    ('local', u'Subir archivo de video'),
    ('externo', u'Importar video desde un sitio web'),
)

class VideoQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de videos
    """
    def publicos(self):
        return self.filter(
                procesamiento=Video.PROCESAMIENTO.listo,
                #estado=Video.ESTADO.publicado,
                fecha__lte=datetime.now()) \
            .select_related('categoria', 'tipo','autor')

class Video(models.Model):
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
    archivo = models.FileField(upload_to='videos', blank=True, null=True)
    imagen = SorlImageField(upload_to='images', blank=True, null=True)
    hls = models.FileField(u'HLS', upload_to='hls', blank=True, null=True)
    resolucion = models.IntegerField(u'resolución máxima',
        db_index=True, blank=True, null=True
        )
    dash = models.FileField(u'DASH', upload_to='hls', blank=True, null=True)
    sprites = models.FileField(upload_to='sprites', blank=True, null=True)
    captions = models.FileField(upload_to='captions', blank=True, null=True)

    # stream info
    duracion = models.DurationField(u'duración', default=timedelta(0))
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)
    original_metadata = JSONField(null=True, blank=True)
    fps = models.FloatField(blank=True, null=True, default=0, editable=False)

    # editorial
    fecha = models.DateTimeField(db_index=True, default=timezone.now)
    titulo = models.CharField(u'título', max_length=128, blank=True)
    slug = AutoSlugField(
        populate_from='titulo', unique=True, always_update=True
        )
    resumen = models.TextField(blank=True)
    descripcion = models.TextField(u'descripción',
        blank=True, help_text=u'descripción detallada del video'
        )
    transcripcion = models.TextField(u'transcripción', blank=True)
    observaciones = models.TextField(blank=True)

    # ManyToMany
    sitios = models.ManyToManyField('Sitio')
    listas = models.ManyToManyField('Lista',
        blank=True, through='ListaVideo', related_name='videos'
        )
    tags = TaggableManager(u'tags',
        blank=True, help_text=u'Palabras o frases clave separadas por coma'
        )
    
    # Relaciones
    categoria = models.ForeignKey('Categoria', models.SET_NULL, blank=True, null=True)
    tipo = models.ForeignKey('Tipo', models.SET_NULL, blank=True, null=True)
    autor = models.ForeignKey('Autor', models.SET_NULL, blank=True, null=True)

    ciudad = models.CharField(u'ciudad/estado', max_length=255, blank=True)
    pais = CountryField(u'país', blank_label=u'Selecciona país', blank=True)

    # tracking
    fecha_creacion = models.DateTimeField(u'fecha de creación',
        db_index=True, auto_now_add=True
        )
    fecha_modificacion = models.DateTimeField(u'última modificación',
        null=True, blank=True, editable=False, auto_now=True
        )
    fecha_publicacion = MonitorField(u'fecha de publicación',
        monitor='estado', when=['publicado']
        )
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        verbose_name=u'creado por',
        related_name='videos_creados',
        blank=True, null=True
        )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name=u'modificado por',
        related_name='videos_modificados',
        blank=True, null=True
        )
    tracker = FieldTracker()

    # Default Manager
    objects = VideoQuerySet.as_manager()

    def __unicode__(self):
        if self.is_listo:
            return u'{0}: {1}'.format(self.pk, self.titulo or u'[Sin título]')
        else:
            return u'{0}: [{1}]'.format(
                self.pk, self.PROCESAMIENTO[self.procesamiento]
                )

    def get_absolute_url(self):
        return reverse('video',
            kwargs={ 'video_slug': self.slug, 'video_uuid': self.uuid }
            )

    def get_admin_form_tabs(self):
        return GET_VIDEO_TABS(self)

    '''
       Properties
    '''
    @property
    def uuid(self):
        """
        strong con ID aumentado a 8 caracteres, siempre de longitud UUID_LENGTH
        """
        LENGTH = 8
        if self.pk:
            str_pk = str(self.pk)
            long_uuid = shortuuid.ShortUUID(alphabet="123456789").uuid(str_pk)
            return "{0}0{1}".format(long_uuid[:LENGTH-1-len(str_pk)], str_pk)


    @property
    def query_procesamiento(self):
        from subprocess import call, check_output, CalledProcessError

        status_path = os.path.join(settings.TEMP_ROOT, 'status', self.uuid)
        vstats_path = os.path.join(settings.TEMP_ROOT, 'vstats', self.uuid)

        result = {'status': None}

        if os.path.exists(status_path):
            with open(status_path, 'r') as status_file:
                status_list = status_file.read().split()

            if status_list:
                result['status'] = status_list[0]

                if status_list[0] == 'download':  # download has begun
                    result['progress'] = float(status_list[1])
                elif status_list[0] == 'valid':
                     # download has finished and compreession started
                    result['total'] = float(status_list[1])
                    try:
                        tailcmd = ['tail', '-2', vstats_path]
                        vstats_line = check_output(tailcmd).split("\n")[0]
                        result['seconds'] = float(vstats_line.split()[9])
                        result['progress'] = 100 * round(
                            result['seconds']/result['total'], 2
                            )
                    except (CalledProcessError, IndexError):
                        # No vstats file or invalid
                        result['seconds'] = 0
                        result['progress'] = 0
                elif status_list[0] == 'done':
                    result['id'] = int(status_list[1])
                elif status_list[0] == 'error':
                    result['code'] = int(status_list[1])
                    result['msg'] = ' '.join(status_list[2:])
        return result

    
    @property
    def descripcion_plain(self):
        return strip_tags(self.descripcion)

    @property
    def url(self):
        return self.get_absolute_url()

    '''
    Estado
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
    Duracion
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

    @property
    def hls_url(self):
        return '{0}opts/hls/{1}/playlist.m3u8'.format(
            settings.MEDIA_URL, self.pk
            )

    @property
    def sprites_url(self):
        return '{0}opts/sprites/{1}/s.vtt'.format(
            settings.MEDIA_URL, self.pk
            )

    class Meta:
        '''
        Video Meta class
        '''
        ordering = ('-fecha', '-fecha_creacion', '-pk')



LISTA_TIPO_CHOICES = Choices(
    ('tematico', u'Lista temática'),
    ('destacado', u'Lista de destacados'),
    ('serie', u'Serie'),
)

LISTA_LAYOUT_CHOICES = Choices(
    ('auto', u'Automático'),
    ('c100', u'1 columna'),
    ('c50', u'1 o 2 columnas'),
    ('c33', u'Hasta 3 columnas'),
    ('c25', u'Hasta 4 columnas'),
)

class ListaQuerySet(models.query.QuerySet):
    """
    Lógica de consulta de Listas
    """
    def destacados(self, categoria=None):
        qs = self.filter(tipo=Lista.TIPO.destacado, usar_web=True)
        if categoria:
            return qs.filter(categoria=categoria)
        else:
            return qs.filter(categoria__isnull=True)
        

class Lista(models.Model):
    TIPO = LISTA_TIPO_CHOICES
    tipo = StatusField(u'tipo de lista', choices_name='TIPO',
                       default=TIPO.tematico)
    LAYOUT = LISTA_LAYOUT_CHOICES
    layout = StatusField(choices_name='LAYOUT', default=LAYOUT.auto,
        help_text=u'<em>Automático</em> ajusta el layout dependiendo del ' \
                  u'número de videos que contenga la lista'
        )
    slug = AutoSlugField(populate_from='nombre', unique_with=['tipo'],
                         always_update=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(u'descripción', blank=True)

    usar_nombre = models.BooleanField(default=True)
    usar_descripcion = models.BooleanField(default=True)
    # plataformas
    usar_web = models.BooleanField(u'usar en sitio web',
        default=True, db_index=True
        )
    usar_movil = models.BooleanField(u'usar en móviles',
        default=True, db_index=True
        )
    usar_tv = models.BooleanField(u'usar en smart TV',
        default=True, db_index=True
        )
    # publicidad
    ads_web = models.BooleanField(u'publicidad en sitio web',
        default=True, db_index=True
        )
    ads_movil = models.BooleanField(u'publicidad en móviles',
        default=True, db_index=True
        )
    ads_tv = models.BooleanField(u'publicidad en smart TV',
        default=True, db_index=True
        )
    categoria = models.ForeignKey('Categoria', models.CASCADE,
        blank=True, null=True, verbose_name=u'Categoría',
        help_text=u'Dejar vacío para asignar al home/portada'
        )
    fecha_creacion = models.DateTimeField(u'fecha de creación',
        db_index=True, editable=False, auto_now_add=True
        )
    fecha_modificacion = models.DateTimeField(u'última modificación',
        null=True, blank=True, auto_now=True, editable=False
        )
    tags = TaggableManager(u'tags', blank=True,
        help_text=u'Estos tags se aplican a todos los videos de la lista',
        )
    orden = models.PositiveIntegerField()

    objects = ListaQuerySet.as_manager()

    @property
    def descripcion_plain(self):
        return strip_tags(self.descripcion)

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ['orden', '-fecha_creacion', '-pk']


class ListaVideo(models.Model):
    video = models.ForeignKey(Video, related_name='enlistado')
    lista = models.ForeignKey(Lista, related_name='enlistado')
    orden = models.PositiveIntegerField()

    class Meta:
        ordering = ['orden', '-pk']
        verbose_name = u'Video en lista'
        verbose_name_plural = u'Videos en lista'
        unique_together = (("video", "lista"),)


class Tipo(models.Model):
    slug = AutoSlugField(populate_from='nombre', unique=True)
    nombre = models.CharField(max_length=64, blank=True)
    nombre_plural = models.CharField(max_length=64, blank=True)
    descripcion = models.TextField(u'descripción', blank=True)
    REPRODUCCION = REPRODUCCION_CHOICES
    reproduccion = StatusField(u'reproducción',
        choices_name='REPRODUCCION', default=REPRODUCCION.auto
        )
    orden = models.PositiveIntegerField()

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ['orden', '-pk']
        verbose_name = 'tipo de video'
        verbose_name_plural = 'tipos de video'


class Categoria(models.Model):
    slug = AutoSlugField(populate_from='nombre', unique=True)
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField()

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ['orden']
        verbose_name = u'categoría'
        verbose_name_plural = 'categorías'


class Autor(models.Model):
    slug = AutoSlugField(populate_from='nombre', unique=True)
    nombre = models.CharField(max_length=128)
    REPRODUCCION = REPRODUCCION_CHOICES
    reproduccion = StatusField(u'política de reproducción',
        choices_name='REPRODUCCION',
        default=REPRODUCCION.auto
        )
    orden = models.PositiveIntegerField()
    
    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ['orden', '-pk']
        verbose_name_plural = u'autores'



class Sitio(models.Model):
    slug = AutoSlugField(populate_from='nombre', unique=True, always_update=True)
    nombre = models.CharField(max_length=128)
    url = models.URLField(blank=True, null=True)
    REPRODUCCION = REPRODUCCION_CHOICES
    reproduccion = StatusField(u'política de reproducción',
        choices_name='REPRODUCCION', default=REPRODUCCION.auto
        )
    orden = models.PositiveIntegerField()

    def __unicode__(self):
        return self.nombre


# class Distribucion(models.Model):
#     TEMPLATE_CHOICES = (
#         ('notificacion-ficha-tecnica', u'Notificación con ficha técnica'),
#         ('notificacion-sencilla', u'Notificación snecilla')
#     )
#     descripcion = models.CharField(u'nombre/descripción', max_length=255)
#     activo = models.BooleanField(default=True)
#     fecha_desde = models.DateTimeField(null=True, blank=True, help_text=u'Realizar distribución a partir la fecha seleccionada')
#     fecha_hasta = models.DateTimeField(null=True, blank=True, help_text=u'Realizar distribución hasta la fecha seleccionada')
#     configuracion = models.TextField(u'configuración', blank=True, null=True)
#     email = models.CharField(max_length=255, blank=True, null=True, help_text=u'Uno o varios emails separados por comas con el formato:  Nombre Primer Destinatario &lt;usuario@dominio.com&gt;, Nombre Segundo Destinatario &lt;otro@dominio.com&gt;, ...')
#     email_template = models.CharField(u'Plantilla e-mail', max_length=255, choices=TEMPLATE_CHOICES, blank=True, null=True, help_text=u'Plantilla a usar para dar formato a los mensajes')
#     ftp_host = models.CharField(u'Host FTP', max_length=255, blank=True, null=True)
#     ftp_port = models.CharField(u'Puerto FTP', max_length=255, blank=True, null=True)
#     ftp_dir = models.CharField(u'Directorio FTP', max_length=255, blank=True, null=True)
#     ftp_user = models.CharField(u'Usuario FTP', max_length=255, blank=True, null=True)
#     ftp_pass = models.CharField(u'Contraseña FTP', max_length=255, blank=True, null=True)
#     # campos para reglas
#     texto = models.CharField(max_length=255, blank=True, null=True, help_text=u'Videos que contengan el texto especificado en el título o descripción')
#     tipos = models.ManyToManyField(Tipo, blank=True)
#     categorias = models.ManyToManyField(Categoria, blank=True)
#     programas = models.ManyToManyField(Programa, blank=True)
#     tipos_programa = models.ManyToManyField(TipoPrograma, blank=True)
#     temas = models.ManyToManyField(Tema, blank=True)
#     paises = models.ManyToManyField(Pais, blank=True, verbose_name=u'países')
#     corresponsales = models.ManyToManyField(Corresponsal, blank=True)
#     con_corresponsal = models.BooleanField(default=False, help_text=u'Elegur unicamente videos que tengan corresponsal asociado')
#     series = models.ManyToManyField(Serie, blank=True)

#     def get_email_dict(self):
#          email = map(lambda x: x.strip(), self.email.split(','))
#          email = map(lambda x: parseaddr(x), email)
#          return email

#     def get_ftp_port(self):
#         return self.ftp_port or '21'

#     def get_videos_distribuibles(self, threshold_days=2):
#         videos = Video.objects.filter(procesado=True, publicado=True)
#         if self.fecha_desde:
#             videos = videos.filter(fecha__gte=self.fecha_desde)
#         if self.fecha_hasta:
#             videos = videos.filter(fecha__lte=self.fecha_hasta)
#         if self.texto:
#             videos = videos.filter(Q(titulo__icontains=self.texto) | Q(descripcion__icontains=self.texto))
#         if self.con_corresponsal:
#             videos = videos.exclude(corresponsal__isnull=True)
#         if self.tipos.exists():
#             videos = videos.filter(tipo__in=self.tipos.values('pk'))
#         if self.categorias.exists():
#             videos = videos.filter(categoria__in=self.categorias.values('pk'))
#         if self.programas.exists():
#             videos = videos.filter(programa__in=self.programas.values('pk'))
#         if self.tipos_programa.exists():
#             videos = videos.filter(programa__tipo__in=self.tipos_programa.values('pk'))
#         if self.temas.exists():
#             videos = videos.filter(tema__in=self.temas.values('pk'))
#         if self.paises.exists():
#             videos = videos.filter(pais__in=self.paises.values('pk'))
#         if self.corresponsales.exists():
#             videos = videos.filter(corresponsal__in=self.corresponsales.values('pk'))
#         if self.series.exists():
#             videos = videos.filter(serie__in=self.series.values('pk'))

#         return videos.exclude(fecha__lte=datetime.datetime.now() - datetime.timedelta(days=threshold_days))

#     def parseConfiguracion(self):
#         import ConfigParser
#         import StringIO

#         buf = StringIO.StringIO("[root]\n"+self.configuracion)
#         config = ConfigParser.ConfigParser()

#         return config.readfp(buf).items('root')

#     def __unicode__(self):
#         return u'Distribución %s: %s' % (self.pk, self.descripcion)

#     class Meta:
#         verbose_name = u'notificación/distribución'
#         verbose_name_plural = u'notificaciones/distribuciones'


# class Distribuido(models.Model):
#     STATUS_CHOICES = (
#         (1, 'Instrucción recibida'),
#         (2, 'Iniciado'),
#         (3, 'Completado'),
#         (4, 'Error'),
#     )
#     fecha = models.DateTimeField(auto_now_add=True)
#     status = models.IntegerField(choices=STATUS_CHOICES, default=1)
#     distribucion = models.ForeignKey(Distribucion, related_name='distribuidos')
#     video = models.ForeignKey(Video)

#     def __unicode__(self):
#         return u'Video distribuido #%d (%s) por distribución (%s)' % (self.pk, self.video, self.distribucion)

#     class Meta:
#         verbose_name = u'video notificado/distribuído'
#         verbose_name_plural = u'videos notificados/distribuídos'
#         ordering = ['-fecha']
