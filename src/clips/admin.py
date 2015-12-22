# -*- coding: utf-8 -*- #
from clips.models import *
from functools import reduce
from operator import and_, or_
from django.contrib import admin
from django.contrib.auth.models import User
from models import *
from django.http import HttpResponse
from django.template.defaultfilters import filesizeformat, date, linebreaksbr, slugify
from django.conf import settings
from os import path
from datetime import datetime, timedelta
from django.utils import timezone
from django import forms
from django.conf.urls import patterns
from django.core.cache import cache
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
import re


admin.site.site_header = u'Administración de Videos ' + settings.SITE_NAME
admin.site.site_title = u'Videos ' + settings.SITE_NAME
admin.site.index_title = u'Administración'
admin.site.site_url = None


def normalize_logs(logs, users):
    logs = list(logs)
    for i in range(0, len(users)-1):
        if i >= len(logs) or logs[i]['user'] != users[i].id:
            logs.insert(i, {'user': users[i].id, 'count': 0})
    return logs


class ClipAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'informacion', 'actividad')
    list_filter = ['publicado', 'transferido', 'tipo', 'fecha', 'categoria', 'programa', 'corresponsal', 'tema', 'usuario_publicacion', 'usuario_creacion', 'pais']
    date_hierachy = 'fecha'
    search_fields = ['id', 'titulo', 'descripcion']
    actions = ['marcar_publicado', 'marcar_no_publicado', 'cambiar_thumbnail']
    list_per_page = 20
    save_on_top = True
    ordering = ('-fecha', '-fecha_creacion',)
    change_list_template = 'admin/clips/clip/change_list.html'
    change_form_template = 'admin/clips/clip/change_form.html'
    readonly_fields = ('slug', 'transferido')

    fieldsets = (
        # ('Recorte', {
        #     'classes': ('collapse',),
        #     'fields': ('recorte_inicio', 'recorte_final')
        # }),
       # (u'Vistas', {
       #       'classes': (''),
       #      'fields': ('yt_viewcount', 'fecha_yt_viewcount', 'indice_yt_viewcount', 'seleccionado'),
       #  }),
        ('Básico', {
            'classes': ('wide',),
            'fields': ('origen', 'tipo', 'fecha', 'titulo', 'descripcion', 'hashtags')
        }),
        (u'Clasificación', {
            'classes': ('wide'),
            'fields': ('categoria', 'programa', 'tema', 'pais', 'corresponsal', 'serie', 'capitulo')
        }),
        ('Estado', {
            'classes': ('wide',),
            'fields': ('publicado', 'observaciones', 'transferido', 'slug')
        }),
        ('Archivos', {
            'classes': ('collapse',),
            'fields': ('archivo', 'imagen'),
        }),
    )

    class Media:
        js = (
            '//content.jwplatform.com/libraries/z1PvIY5j.js',
        )

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        import datetime
        instance = form.save(commit=False)

        marcar_modificado = False

        usuario_creacion = getattr(instance, 'usuario_creacion', None)
        usuario_redaccion = getattr(instance, 'usuario_redaccion', None)
        usuario_publicacion = getattr(instance, 'usuario_publicacion', None)

        # el video es nuevo
        if not usuario_creacion:
            instance.usuario_creacion = request.user.username

        # Se ha redactado
        elif not usuario_redaccion and instance.titulo and instance.descripcion:
            instance.usuario_redaccion = request.user.username
            instance.fecha_redaccion = datetime.datetime.now()

        # Se a modificado/corregido
        else:
            marcar_modificado = True

        if instance.publicado:
            if instance.titulo and (instance.descripcion or instance.tipo.slug in ['programa', 'infografia']) or instance.usuario_creacion == 'Admin':
                if not usuario_publicacion and instance.tipo.slug not in ['programa',]:
                    instance.usuario_publicacion = request.user.username
                    instance.fecha_publicacion = datetime.datetime.now()
                    # TODO: será necesario marcar modificado cuando solo se publica?
                    marcar_modificado = False
            else:
                instance.publicado = False
                self.message_user(request, 'Se modificó el clip, pero NO se marcó como publicado porque aún no tiene todos los campos requeridos')
        else:
            instance.usuario_publicacion = None
            instance.fecha_publicacion = None

        if marcar_modificado and not instance.usuario_modificacion == 'FTP':
            instance.usuario_modificacion = request.user.username
            instance.fecha_modificacion = datetime.datetime.now()

        if instance.ciudad and instance.pais:
            instance.geotag = None

        if request.FILES:
            # marcar como archivo no procesado
            instance.duracion = datetime.time(0,0)
            instance.transferido = False

        instance.save()
        form.save_m2m()

        return instance

    def get_urls(self):
        urls = super(ClipAdmin, self).get_urls()
        return urls
        custom_urls = patterns('',
            (r'^estadisticas/(?P<grafica>.+)/(?P<desde>.+)/(?P<hasta>.+)/$', self.clip_estadisticas_data_view),
            (r'^estadisticas/(?P<grafica>.+)/$', self.clip_estadisticas_data_view),
            (r'^estadisticas/$', self.clip_estadisticas_view),
            (r'^reportes/(?P<grafica>.+)/(?P<desde>.+)/(?P<hasta>.+)/$', self.clip_reportes_data_view),
            (r'^reportes/(?P<grafica>.+)/$', self.clip_reportes_data_view),
            (r'^reportes/$', self.clip_reportes_view),
            (r'^arreglar-error-archivo/$', self.arreglar_archivo_vacio),
        )
        return custom_urls + urls

    def marcar_publicado(self, request, queryset):
        from django.contrib import messages
        import datetime

        invalidos = []
        validos = []
        for clip in queryset:
            if clip.titulo:
                clip.publicado = True
                if not clip.usuario_publicacion:
                    clip.usuario_publicacion = request.user.username
                    clip.fecha_publicacion = datetime.datetime.now()
                clip.save()
                validos.append(clip)
            else:
                invalidos.append(clip)
        if len(validos) > 0:
            self.message_user(request, u"%s clip/s marcados como publicado/s con éxito" % queryset.count())
        if len(invalidos) > 0:
            messages.warning(request, u"%d clip/s NO fueron publicado/s debido a que no tiene/n título" % len(invalidos))
    marcar_publicado.short_description = u"Marcar clip/s seleccionados como publicado/s"

    def marcar_no_transferido(self, request, queryset):
        queryset.update(transferido=False)
        self.message_user(request, u"%s clip/s marcados para volver a transferir con éxito" % queryset.count())
    marcar_no_transferido.short_description = u"Volver a tranferir clip/s seleccionado/s"

    def cambiar_thumbnail(self, request, queryset):
        import random
        from django.core.files.base import ContentFile
        from subprocess import call

        for clip in queryset:
            nombre_base = '%s-%s' % (datetime.now().strftime('%F'), clip.pk)
            nombre_imagen = 'imagen-%s.jpg' % nombre_base

            offset = (clip.duracion.minute*60 + clip.duracion.second) * random.random()

            cmd_imagen = 'ffmpeg -y -ss %d -i %s -vframes 1 -an /tmp/%s' % (offset, clip.archivo.path, nombre_imagen)
            status = call(cmd_imagen, shell=True)
            imagen_content = ContentFile(open('/tmp/%s' % nombre_imagen, 'r').read())
            clip.imagen.save(nombre_imagen, imagen_content)
            os.remove('/tmp/%s' % nombre_imagen)

            clip.save()

        self.message_user(request, u"Se generaron thumbnails diferentes para %s clips" % queryset.count())
    cambiar_thumbnail.short_description = u"Generar thumbnail diferente para clips seleccionado/s"

    def marcar_no_publicado(self, request, queryset):
        queryset.update(publicado=False, usuario_publicacion=None, fecha_publicacion=None)
        self.message_user(request, u"%s clips marcados como no publicado/s con éxito" % queryset.count())
    marcar_no_publicado.short_description = u"Marcar clips seleccionados como no publicado/s"

    def servicios_(self, obj):
        if not obj.publicado:
            return 'N/A'

        html = u'<table style="font-size:90%;margin:0 !important;" border="1" cellspacing="0" cellpadding="3">'

        servicios = obj.tipo.servicios.filter(activo=True)
        if obj.programa and obj.tipo.slug == 'programa':
            servicios_programa = obj.programa.servicios.filter(activo=True)
            combined = reduce(or_, [servicios], servicios_programa)
            servicios = combined.exclude(pk__in=obj.programa.excluir_servicios.all()).distinct()
        for servicio in servicios:
            try:
                sc = obj.servicioclip_set.get(servicio=servicio)
                html+= u'<tr><th>%s</th> <td>%s</td></tr>' % (servicio.nombre, sc.get_estado_display())
            except:
                html+= u'<tr><th>%s</th> <td>Sin procesar</td></tr>' % servicio.nombre
        html+= u'</table>'
        return html
    servicios_.allow_tags=True

    def actividad(self, obj):
        html = u'<table style="width:200px; font-size:90%;margin:0 !important;" border="1" cellspacing="0" cellpadding="3">'

        # Flujo, acciones y fechas

        html+= u'<tr><th>Vistas</th> <td>%s</td></tr>' % obj.vistas

        html+= u'<tr><th>Publicado</th> <td><img src="/static/admin/img/icon-%s.gif" /> <b>%s</b><br />%s</td></tr>' % (obj.publicado and 'yes' or 'no', obj.usuario_publicacion or '', date(obj.fecha_publicacion, "j/b/Y P"))
        #if obj.slug:
        #    html+= u'<tr><th>Sincronizado</th> <td><img src="/static/admin/img/icon-%s.gif" />' % (obj.en_api() and 'yes' or 'no')
        if obj.usuario_redaccion:
            html+= u'<tr><th>Redactado</th> <td><b>%s</b><br />%s</td></tr>' % (obj.usuario_redaccion, date(obj.fecha_redaccion, "j/b/Y P"))
        if obj.usuario_modificacion:
            html+= u'<tr><th>Modificado</th> <td><b>%s</b><br />%s</td></tr>' % (obj.usuario_modificacion, date(obj.fecha_modificacion, "j/b/Y P"))
        html+= u'<tr><th>Cargado</th> <td><b>%s</b><br />%s</td></tr>' % (obj.usuario_creacion, date(obj.fecha_creacion, "j/b/Y P"))

        if not obj.transferido:
            html+= u'<tr><th>Procesado</th> <td><img src="/static/admin/img/icon-%s.gif" /></td></tr>' % ('no', 'yes')[obj.transferido]
        html+= u'</table>'

        if obj.publicado:
            html += u'<br/><table style="font-size:90%;margin:0 !important;" border="1" cellspacing="0" cellpadding="3">'
            html += self.servicios_(obj)

        return html
    actividad.allow_tags=True
    actividad.admin_order_field='fecha_creacion'

    # def tags_(self, obj):
    #     if not obj.tags:
    #         return ''
    #     new_tags = ['&quot;%s&quot;' % tag for tag in obj.tags.split(', ')]
    #     return u'<div style="width:200px">%s</div>' % ', '.join(new_tags)
    # tags_.allow_tags=True

    def fecha_(self, obj):
        return date(obj.fecha, "j/b/Y P")
    fecha_.admin_order_field='fecha'

    def fecha_creacion_(self, obj):
        return obj.fecha_creacion.isoformat()
    fecha_creacion_.admin_order_field='fecha_creacion'

    def descripcion_(self, obj):
        html = u'<p>%s</p>' % obj.descripcion
        #if obj.slug:
        #    html+= u'<p>%s</p>' % _clip_url(obj)
        if obj.observaciones:
            html+= '<p style="background-color:#ADD8E6; padding:2px; font-size:95%%; font-weight: bold;">%s</p>' % linebreaksbr(obj.observaciones)
        # if obj.ultimo:
        #     html = '<strong><big style="size: 15px;color:darkgreen;"><p>CLIP PRINCIPAL</p></big>' + html + '</strong>'

        html += '''
            <div id="pong-%s"></div>
            <script>
            var pong = function() {
                $.getJSON("/pong/", { type: "clip", id: "%s" }, function(data) {
                    if (data.length) {
                        $("#pong-%s").html("<p style=\'background:gold;\'>Editando ahora: " + data.join(", ") + "</p>");
                    } else {
                        $("#pong-%s").html("");
                    }
                })
            }
            //setInterval(pong, 90000);
            //pong();
            </script>''' % (obj.id, obj.id, obj.id, obj.id)

        return '<div style="text-align:center; font-size:1.2em;">%s</div>' % html

    descripcion_.allow_tags=True

    def informacion(self, obj):
        html = u'<table style="width: 225px !important; margin:0 !important;font-size:90%%;" border="1" cellspacing="0" cellpadding="3">'

        if obj.tipo:
            html+= u'<tr><td colspan="2" align="center" style="font-size:170%%;font-seight:bold;;">%s</td></tr>' % obj.tipo
        html+= '<tr><th>Origen</th> <td style="width:100%%">%s</td></tr>' % obj.get_origen_display()
        if obj.fecha:
            if obj.fecha > timezone.now():
                html+= '<tr><td colspan="2" align="center" style="background:yellow;">FUTURO</td></tr>'
            html+= '<tr><th>Fecha</th> <td style="width:100%%">%s</td></tr>' % date(obj.fecha, "j/b/Y P")
        if obj.tema:
            html+= u'<tr><th>Tema</th> <td>%s</td></tr>' % obj.tema
        if obj.categoria:
            html+= u'<tr><th>Categoria</th> <td>%s</td></tr>' % obj.categoria
        if obj.pais:
            html+= u'<tr><th>País</th><td>%s</td></tr>' % obj.pais
        if obj.corresponsal:
            html+= u'<tr><th>Corresponsal</th> <td>%s</td></tr>' % obj.corresponsal
        if obj.programa:
            html+= u'<tr><th>Programa</th> <td>%s</td></tr>' % obj.programa
        if obj.serie:
            html+= u'<tr><th>Serie</th> <td>%s</td></tr>' % obj.serie
        if obj.capitulo:
            html+= u'<tr><th>Capítulo</th> <td>%s</td></tr>' % obj.capitulo
        if obj.hashtags:
            html+= u'<tr><th>Hashtags</th> <td>%s</td></tr>' % obj.hashtags

        html+= u'</table>'
        return html
    informacion.allow_tags=True

    def video(self, obj):
        from django.template import Context, Template

        if obj.publicado:
            html = u'<div style="font-size:1.3em; line-height:1.3em; font-weight: bold; margin:0.5em; text-align: center;"><a target="_blank" href="%s" title="%s">%s</a></div>' % (obj.make_url(), obj.make_url(), obj.titulo)
        else:
           html = u'<div style="font-size:1.3em; line-height:1.3em; text-align:center; margin:0.5em;">%s</div>' % obj.titulo

        if obj.fps == -2.0:
            return html + u'<p style="width: 128px;padding:1.2em 0.5em;"><em><strong>[Atención]</strong> Imposible obtener datos de video. Formato inválido. Sólo MP4 (códec h264)</em></p>'
        
        video_url = obj.get_archivo().url

        thumbnail_url = obj.thumbnail_grande()

        if obj.archivo:
            size = cache.get('archivo-filesize' + obj.archivo.name, None)
            if size != None:
                v_filesize = size
            else:
                if os.path.exists(obj.archivo.path):
                    v_filesize = filesizeformat(obj.archivo.size)
                    if v_filesize: cache.set('archivo-filesize' + obj.archivo.name, v_filesize, 86400)
                else:
                    v_filesize = '---'
                    video_url = ''
                    #video_url = 'http://media.openmultimedia.biz/%s' % obj.get_archivo().url.replace('media/', '')

        html += u'''
            <div style="margin: 0 auto; max-width: 80%%; padding: 5px;"><div id="player-%d">Cargando player...</div></div>
            <script type="text/javascript">
            var playerInstance = jwplayer("player-%d");
            playerInstance.setup({
                file: "%s",
                image: "%s",
            });
            </script>

            <div style="text-align:center; padding-bottom:1em;"><p>Duración: %s</p><a href="%s" title="%s" target="_blank"><em>Descarga video: %s</em></a></div>
        ''' % (obj.pk, obj.pk, video_url, thumbnail_url, obj.duracion.isoformat(), video_url, path.basename(obj.archivo.name), v_filesize)

        # Descripcion
        html += '<small>%s</small>' % self.descripcion_(obj)

        return html
    video.allow_tags=True
    video.admin_order_field = 'video'


class ServicioClipAdmin(admin.ModelAdmin):
    list_display = ('clip', 'servicio', 'estado', 'fecha_creacion')
    list_filter = ('clip__tipo', 'clip__programa', 'servicio', 'estado', 'fecha_creacion')
    readonly_fields = ('clip', 'servicio', 'estado')
    list_per_page = 100

    def has_add_permission(self, request):
        return False
admin.site.register(ServicioClip, ServicioClipAdmin)


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'contrasena', 'activo', 'perfil_publico')
    list_editable = ('activo',)

    def perfil_publico(self, obj):
        return ''


class TipoProgramaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    list_editable = ('orden',)


class TipoClipAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nombre_plural', 'descripcion', 'descargable', 'servicios_', 'orden')
    list_editable = ('orden',)
    filter_horizontal = ['servicios']
    list_filter = ('servicios',)

    def servicios_(self, obj):
        return ', '.join(unicode(x.slug) for x in obj.servicios.all())


class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'imagen_', 'activo', 'tipo', 'servicios_', 'orden')
    list_editable = ('orden',)
    filter_horizontal = ['servicios', 'excluir_servicios']
    list_filter = ('activo', 'tipo', 'servicios',)

    def imagen_(self, obj):
        if not obj.imagen:
            return 'SIN IMAGEN'
        else:
            return '<img src="%s" height="75" />' % obj.imagen.url
    imagen_.allow_tags=True

    def servicios_(self, obj):
        servicios = ', '.join(unicode(x.slug) for x in obj.servicios.all())
        no_servicios = ', '.join(unicode(x.slug) for x in obj.excluir_servicios.all())
        if no_servicios:
            return u'%s. (Excluye: %s)' % (servicios, no_servicios)
        if servicios:
            return servicios


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    list_editable = ('orden',)


class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'ubicacion')
    list_filter = ('ubicacion',)
    # alphabet_filter = 'nombre'
    # DEFAULT_ALPHABET = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class CorresponsalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'twitter', 'email', 'activo', 'orden')
    list_editable = ('orden',)
    list_filter = ('pais', 'activo')
    alphabet_filter = 'nombre'
    DEFAULT_ALPHABET = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class ClipInline(admin.TabularInline):
    model = Clip


class TemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'orden', 'descripcion', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'activo')
    fk_service = ['nombre']
    list_editable = ('orden', 'activo')
    search_fields = ['id', 'nombre', 'descripcion']
    alphabet_filter = 'nombre'
    DEFAULT_ALPHABET = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class SerieAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ['id', 'nombre', 'descripcion']
admin.site.register(Serie, SerieAdmin)


class DistribucionAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'activo', 'canales', 'criterios',
                    'clips_elegibles', 'clips_distribuidos', 'ultimo_dia')
    list_filter = ('activo', 'email', 'tipos', 'corresponsales')
    filter_horizontal = ['tipos', 'categorias', 'programas', 'tipos_programa',
                         'temas', 'paises', 'corresponsales', 'series']
    fieldsets = (
        (None, {
            'fields': ('descripcion', 'activo')
        }),
        (u'Notificación por e-mail', {
            'classes': ('collapse',),
            'fields': ('email', 'email_template')
        }),
        (u'Cargas de archivo a FTP remoto', {
            'classes': ('collapse',),
            'fields': ('ftp_host', 'ftp_port', 'ftp_dir', 'ftp_user', 'ftp_pass')
        }),
        (u'Reglas de selección', {
            'classes': ('collapse',),
            'fields': ('fecha_desde', 'fecha_hasta', 'con_corresponsal',
                       'texto', 'tipos', 'categorias', 'programas', 'tipos_programa',
                       'temas', 'paises', 'corresponsales', 'series')
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(DistribucionAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'email':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

    def clips_elegibles(self, obj):
        return obj.get_clips_distribuibles().count()

    def clips_distribuidos(self, obj):
        return obj.distribuidos.count()

    def ultimo_dia(self, obj):
        return obj.distribuidos.filter(fecha__gt=datetime.now() - timedelta(hours=24)).count()

    def criterios(self, obj):
        result = []
        if obj.texto:
            result.append(u'<strong>Búsqueda de texto</strong>: %s' % obj.texto)
        if obj.con_corresponsal:
            result.append(u'<strong>Con corresponsal</strong>: Sí')

        relations = ('tipos', 'categorias', 'programas', 'tipos_programa',
                     'corresponsales', 'temas', 'paises', 'series',)
        for r in relations:
            objs = getattr(obj, r)
            if objs.exists():
                result.append(u'<strong>%s</strong>: %s' % (r.capitalize(), ', '.join(map(lambda x: unicode(x), objs.all()))))

        if obj.fecha_desde:
            result.append(u'<strong>Fecha de inicio:</strong> %s' % obj.fecha_desde)
        if obj.fecha_hasta:
            result.append(u'<strong>Fecha final:</strong> %s' % obj.fecha_hasta)

        return '<br />'.join(result)
    criterios.allow_tags=True

    def canales(self, obj):
        html = ''
        if obj.email:
            html += u'<p><strong>Email:</strong> <em>%s</em>' % obj.email.replace('<', '&lt;').replace('>', '&gt;')
            html += u'<br /><strong>Plantilla:</strong> <em>%s</em></p>' % obj.email_template
        if obj.ftp_host:
            html += u'<p><strong>FTP:</strong> <em>%s (puerto %s)</em>' % (obj.ftp_host, obj.get_ftp_port())
            if obj.ftp_user:
                html += u'<br /><strong>Usuario:</strong> <em>%s</em>' % obj.ftp_user
            if obj.ftp_pass:
                html += u'<br /><strong>Contraseña:</strong> <em>%s</em>' % obj.ftp_pass
            if obj.ftp_dir:
                html += u'<br /><strong>Directorio:</strong> <em>%s</em>' % obj.ftp_dir
            html += u'</p>'
        return html
    canales.allow_tags=True
admin.site.register(Distribucion, DistribucionAdmin)


class DistribuidoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'fecha', 'distribucion', 'clip']
    list_filter = ['distribucion', 'fecha', 'clip__corresponsal']
    readonly_fields = ['clip']
    list_per_page = 50

    def has_add_permission(self, request):
        return False
admin.site.register(Distribuido, DistribuidoAdmin)


admin.site.register(Clip, ClipAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Tema, TemaAdmin)
admin.site.register(TipoClip, TipoClipAdmin)
admin.site.register(TipoPrograma, TipoProgramaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Programa, ProgramaAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Corresponsal, CorresponsalAdmin)
