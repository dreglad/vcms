# -*- coding: utf-8 -*- #
from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify, timesince
from django.core.urlresolvers import reverse
from django.db.models import Q
from email.utils import parseaddr
import uuid
import random
import datetime
import os
from sorl.thumbnail import get_thumbnail, ImageField


class Categoria(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    orden = models.IntegerField()
    nombre = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(Categoria, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        ordering = ['orden']
        verbose_name = u'categoría'
        verbose_name_plural = 'categorías'



class Tema(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    orden = models.IntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(u'descripción', blank=True, null=True)
    link = models.URLField(blank=True, editable=False, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, editable=False)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(Tema, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.nombre)

    class Meta:
        ordering = ['-orden', '-id']



class Serie(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(u'descripción', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(Serie, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.nombre


class TipoClip(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    orden = models.IntegerField()
    nombre = models.CharField(max_length=100, blank=True, null=True)
    nombre_plural = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(u'descripción', blank=True, null=True)
    servicios = models.ManyToManyField('Servicio')
    descargable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(TipoClip, self).save(*args, **kwargs)

    class Meta:
        ordering = ['orden']
        verbose_name = 'tipo de clip'
        verbose_name_plural = 'tipos de clip'



class TipoPrograma(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    orden = models.IntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(TipoPrograma, self).save(*args, **kwargs)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'tipo de programa'
        verbose_name_plural = 'tipos de programa'


def upload_programa_imagen_to(instance, filename):
    nombre, ext = os.path.splitext(filename)
    if instance.pk:
        ext = "-%s%s" % (instance.pk, ext)
    return 'images/programa-%s' % (uuid.uuid4(), ext)

class Programa(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    orden = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    imagen = ImageField(upload_to=upload_programa_imagen_to, blank=True, null=True)
    descripcion = models.TextField(u'descripción', blank=True, null=True)
    playlist = models.CharField(max_length=100, blank=True, null=True)
    horario = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.ForeignKey(TipoPrograma)
    servicios = models.ManyToManyField('Servicio', help_text=u'Servicios externos a distribuir para clips de este programa')
    excluir_servicios = models.ManyToManyField('Servicio', related_name='programas_excluidos', help_text=u'Servicios externos a excluir en caso de que haya servicios habilitados para todos los clips tipo programa pero que no se desean aplicar a este programa en particular')

    def thumbnail_pequeno(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '150x150', quality=99)
            return im.url
    def thumbnail_mediano(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '300x300', quality=99)
            return im.url
    def thumbnail_grande(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '300x300', quality=99)
            return im.url

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(Programa, self).save(*args, **kwargs)

    class Meta:
        ordering = ['orden', 'nombre']



class Servicio(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)
    contrasena = models.CharField(u'contraseña', max_length=100, blank=True, null=True)
    clips = models.ManyToManyField('Clip', through='ServicioClip')

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(u'%s' % self)
        return super(Servicio, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'servicio externo'
        verbose_name_plural = 'servicios externos'




class ServicioClip(models.Model):
    clip = models.ForeignKey('Clip')
    servicio = models.ForeignKey('servicio')
    estado = models.IntegerField(choices=[(0, u'Procesando'), (1, u'Completo'), (2, u'Error')])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = u'clip cargado a servicio externo'
        verbose_name_plural = u'clips cargados a servicios externos'



class Pais(models.Model):
    UBICACION_AMERICA_LATINA = 0
    UBICACION_AMERICA = 1
    UBICACION_EUROPA = 2
    UBICACION_ASIA = 3
    UBICACION_OCEANIA = 4
    UBICACION_AFRICA = 5
    UBICACION_CHOICES = [
        (UBICACION_AMERICA_LATINA, u'América Latina'),
        (UBICACION_AMERICA, u'América'),
        (UBICACION_EUROPA, u'Europa'),
        (UBICACION_ASIA, u'Asia'),
        (UBICACION_OCEANIA, u'Oceanía'),
        (UBICACION_AFRICA, u'África')
    ]
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=2)
    geotag = models.CharField(max_length=255, blank=True, null=True)
    ubicacion = models.IntegerField(u'ubicación', choices=UBICACION_CHOICES)

    def __unicode__(self):
        return u'%s' % self.nombre

    def save(self):
        self.slug = slugify(self.nombre)
        return super(Pais, self).save()

    class Meta:
        ordering = ['nombre']
        verbose_name = u'país'
        verbose_name_plural = u'países'



class Corresponsal(models.Model):
    slug = models.SlugField(max_length=100, blank=True, null=True, editable=False)
    orden = models.IntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True, help_text=u'Opcional para notificaciones. No será publicado')
    pais = models.ForeignKey(Pais)
    twitter = models.CharField(blank=True, null=True, max_length=30, help_text='Nombre de usuario en Twitter, sin prefijo "@"')
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        return super(Corresponsal, self).save(*args, **kwargs)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name_plural = u'corresponsales'



def upload_clip_archivo_to(instance, filename):
    nombre, ext = os.path.splitext(filename)
    if instance.pk:
        ext = "-%s%s" % (instance.pk, ext)
    return 'clips/video-%s%s' % (uuid.uuid4(), ext)

def upload_clip_imagen_to(instance, filename):
    nombre, ext = os.path.splitext(filename)
    if instance.pk:
        ext = "-%s%s" % (instance.pk, ext)
    return 'images/imagen-%s%s' % (uuid.uuid4(), ext)

def upload_clip_audio_to(instance, filename):
    nombre, ext = os.path.splitext(filename)
    if instance.pk:
        ext = "-%s%s" % (instance.pk, ext)
    return 'clips/audio-%s%s' % (uuid.uuid4(), ext)



class Clip(models.Model):
    ORIGEN_PROPIO = 1
    ORIGEN_YOUTUBE = 2
    ORIGEN_DAILYMOTION = 3
    ORIGEN_CHOICES = (
        (ORIGEN_PROPIO, 'Video propio'),
        (ORIGEN_YOUTUBE, 'Externo: TouTube'),
        (ORIGEN_DAILYMOTION, 'Externo: Dailymotion'),
    )
    slug = models.SlugField(max_length=100, blank=True, null=True, help_text=u'Identificador para la URL del clip, sin espacios ni caracteres especiales')
    tipo = models.ForeignKey(TipoClip)

    origen = models.IntegerField(choices=ORIGEN_CHOICES, default=ORIGEN_PROPIO)

    # estado
    publicado = models.BooleanField(default=False)
    transferido = models.BooleanField(u'procesado', default=False)
    seleccionado = models.BooleanField(default=False, help_text=u'selección del editor')

    fecha = models.DateTimeField()
    titulo = models.CharField(u'título', max_length=70, blank=True, null=True)
    descripcion = models.TextField(u'descripción', blank=True, null=True)

    archivo = models.FileField(upload_to=upload_clip_archivo_to, blank=True, null=True)
    imagen = ImageField(upload_to=upload_clip_imagen_to, blank=True, null=True, help_text=u'Opcional. Si se omite se obtendrá automáticamente')    
    audio = models.FileField(upload_to=upload_clip_audio_to, blank=True, null=True, editable=False)

    duracion = models.TimeField(u'duración', default='00:00', editable=False)
    resolucion = models.IntegerField(null=True, default=0, editable=False)
    sprites = models.IntegerField(null=True, default=0, editable=False)
    fps = models.FloatField(blank=True, null=True, default=0, editable=False)

    # Flujo, acicones y fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=50, blank=True, null=True, editable=False)
    fecha_redaccion = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_redaccion = models.CharField(max_length=50, blank=True, null=True, editable=False)
    fecha_publicacion = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_publicacion = models.CharField(max_length=50, blank=True, null=True, editable=False)
    fecha_modificacion = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_modificacion = models.CharField(max_length=50, blank=True, null=True, editable=False)

    categoria = models.ForeignKey(Categoria, null=True, blank=True)
    programa = models.ForeignKey(Programa, null=True, blank=True)    
    tema = models.ForeignKey(Tema, null=True, blank=True, limit_choices_to={'activo': True})
    pais = models.ForeignKey(Pais, null=True, blank=True)
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    geotag = models.CharField(max_length=255, blank=True, null=True, editable=False)
    corresponsal = models.ForeignKey(Corresponsal, null=True, blank=True)
    hashtags = models.CharField(max_length=255, help_text=u'Hashtags para Twitter, incluir # y espacios entre cada uno, tal como en Twitter', blank=True, null=True)

    serie = models.ForeignKey(Serie, null=True, blank=True)
    capitulo = models.IntegerField(u'capítulo', null=True, blank=True, help_text=u'Número de capítulo (1, 2, 3, ...)')

    observaciones = models.TextField(blank=True, null=True)
    vistas = models.IntegerField(verbose_name="vistas", default=0, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug and self.titulo and self.publicado:
            self.slug = slugify(self.titulo)
            if Clip.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug += '-%d' % (self.pk or random.randint(100000, 999999))

        if not kwargs.pop('skip_fecha_modificacion', False):
            self.fecha_modificacion = datetime.datetime.now()

        return super(Clip, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.titulo:
            return u'%s (%s)' % (self.pk, self.titulo)
        else:
            return u'%s' % self.pk


    def player_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            return '%s%s' % (settings.HOST, reverse('player',kwargs={'clip_id': self.pk}))
        elif self.origen == Clip.ORIGEN_YOUTUBE:
            return 'http://www.youtube.com/embed/%s?' % self.external_id

    def hls_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            if self.resolucion and self.resolucion > 0:
                return '%shls/%d/playlist.m3u8' % (settings.MEDIA_URL, self.pk)

    def archivo_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            return self.archivo.url

    def audio_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            return self.audio.url

    def sprites_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            if self.sprites and self.sprites > 0:
                return '%ssprites/%d/s.vtt' % (settings.MEDIA_URL, self.pk)

    def descarga_url(self):
        if self.origen == Clip.ORIGEN_PROPIO:
            return '%s?download' % self.archivo.url


    def get_archivo(self):
        return self.archivo
    def get_archivo_url(self):
        return self.archivo.url
    def make_url(self):
        return ''
    def navegador_url(self):
        return ''

    def thumbnail_pequeno(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '150x150', crop='center', quality=99)
            return im.url
    def thumbnail_mediano(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '300x300', crop='center', quality=99)
            return im.url
    def thumbnail_grande(self):
        if self.imagen:
            im = get_thumbnail(self.imagen, '300x300', crop='center', quality=99)
            return im.url

    def get_duracion_segundos(self):
        return self.duracion.hour*60*60 + self.duracion.minute*60 + self.duracion.second

    class Meta:
        ordering = ('-fecha', '-fecha_creacion')
        verbose_name = 'clip de video'
        verbose_name_plural = 'clips de video'


class Distribucion(models.Model):
    TEMPLATE_CHOICES = (
        ('notificacion-ficha-tecnica', u'Notificación con ficha técnica'),
        ('notificacion-sencilla', u'Notificación snecilla')
    )
    descripcion = models.CharField(u'nombre/descripción', max_length=255)
    activo = models.BooleanField(default=True)
    fecha_desde = models.DateTimeField(null=True, blank=True, help_text=u'Realizar distribución a partir la fecha seleccionada')
    fecha_hasta = models.DateTimeField(null=True, blank=True, help_text=u'Realizar distribución hasta la fecha seleccionada')
    configuracion = models.TextField(u'configuración', blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True, help_text=u'Uno o varios emails separados por comas con el formato:  Nombre Primer Destinatario &lt;usuario@dominio.com&gt;, Nombre Segundo Destinatario &lt;otro@dominio.com&gt;, ...')
    email_template = models.CharField(u'Plantilla e-mail', max_length=255, choices=TEMPLATE_CHOICES, blank=True, null=True, help_text=u'Plantilla a usar para dar formato a los mensajes')
    ftp_host = models.CharField(u'Host FTP', max_length=255, blank=True, null=True)
    ftp_port = models.CharField(u'Puerto FTP', max_length=255, blank=True, null=True)
    ftp_dir = models.CharField(u'Directorio FTP', max_length=255, blank=True, null=True)
    ftp_user = models.CharField(u'Usuario FTP', max_length=255, blank=True, null=True)
    ftp_pass = models.CharField(u'Contraseña FTP', max_length=255, blank=True, null=True)
    # campos para reglas
    texto = models.CharField(max_length=255, blank=True, null=True, help_text=u'Clips que contengan el texto especificado en el título o descripción')
    tipos = models.ManyToManyField(TipoClip, blank=True)
    categorias = models.ManyToManyField(Categoria, blank=True)
    programas = models.ManyToManyField(Programa, blank=True)
    tipos_programa = models.ManyToManyField(TipoPrograma, blank=True)
    temas = models.ManyToManyField(Tema, blank=True)
    paises = models.ManyToManyField(Pais, blank=True, verbose_name=u'países')
    corresponsales = models.ManyToManyField(Corresponsal, blank=True)
    con_corresponsal = models.BooleanField(default=False, help_text=u'Elegur unicamente clips que tengan corresponsal asociado')
    series = models.ManyToManyField(Serie, blank=True)

    def get_email_dict(self):
         email = map(lambda x: x.strip(), self.email.split(','))
         email = map(lambda x: parseaddr(x), email)
         return email

    def get_ftp_port(self):
        return self.ftp_port or '21'

    def get_clips_distribuibles(self, threshold_days=2):
        clips = Clip.objects.filter(transferido=True, publicado=True)
        if self.fecha_desde:
            clips = clips.filter(fecha__gte=self.fecha_desde)
        if self.fecha_hasta:
            clips = clips.filter(fecha__lte=self.fecha_hasta)
        if self.texto:
            clips = clips.filter(Q(titulo__icontains=self.texto) | Q(descripcion__icontains=self.texto))
        if self.con_corresponsal:
            clips = clips.exclude(corresponsal__isnull=True)
        if self.tipos.exists():
            clips = clips.filter(tipo__in=self.tipos.values('pk'))
        if self.categorias.exists():
            clips = clips.filter(categoria__in=self.categorias.values('pk'))
        if self.programas.exists():
            clips = clips.filter(programa__in=self.programas.values('pk'))
        if self.tipos_programa.exists():
            clips = clips.filter(programa__tipo__in=self.tipos_programa.values('pk'))
        if self.temas.exists():
            clips = clips.filter(tema__in=self.temas.values('pk'))
        if self.paises.exists():
            clips = clips.filter(pais__in=self.paises.values('pk'))
        if self.corresponsales.exists():
            clips = clips.filter(corresponsal__in=self.corresponsales.values('pk'))
        if self.series.exists():
            clips = clips.filter(serie__in=self.series.values('pk'))

        return clips.exclude(fecha__lte=datetime.datetime.now() - datetime.timedelta(days=threshold_days))

    def parseConfiguracion(self):
        import ConfigParser
        import StringIO

        buf = StringIO.StringIO("[root]\n"+self.configuracion)
        config = ConfigParser.ConfigParser()

        return config.readfp(buf).items('root')

    def __unicode__(self):
        return u'Distribución %s: %s' % (self.pk, self.descripcion)

    class Meta:
        verbose_name = u'notificación/distribución'
        verbose_name_plural = u'notificaciones/distribuciones'



class Distribuido(models.Model):
    STATUS_CHOICES = (
        (1, 'Instrucción recibida'),
        (2, 'Iniciado'),
        (3, 'Completado'),
        (4, 'Error'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    distribucion = models.ForeignKey(Distribucion, related_name='distribuidos')
    clip = models.ForeignKey(Clip)

    def __unicode__(self):
        return u'Clip distribuido #%d (%s) por distribución (%s)' % (self.pk, self.clip, self.distribucion)

    class Meta:
        verbose_name = u'clip notificado/distribuído'
        verbose_name_plural = u'clips notificados/distribuídos'
        ordering = ['-fecha']
