# -*- coding: utf-8 -*- #
from datetime import datetime
import json

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Max
from django.forms import ModelForm, RadioSelect, TextInput, FileInput
from django.forms.widgets import CheckboxSelectMultiple
from django.template import loader, Context
from django.utils.safestring import mark_safe
from django_select2.forms import Select2MultipleWidget, Select2Widget
from reversion.admin import VersionAdmin
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import get_thumbnail
from suit.admin import SortableModelAdmin, SortableTabularInline
from suit.widgets import SuitSplitDateTimeWidget, AutosizedTextarea
from suit_redactor.widgets import RedactorWidget

from .forms import FilestackWidget, AdminImageWidget
from .models import *

RESUMEN_REDACTOR_OPTIONS = {
    'toolbar': False,
    'lang': 'es',
    'pasteLinks': False,
    'pasteImages': False,
    'pasteBlock': [],
    'pasteInline': [],
    'minHeight': 50,
}
DESCRIPCION_REDACTOR_OPTIONS = {
    'buttons': ['bold', 'italic', 'deleted', 'horizontalrule', 'lists',],
    'lang': 'es',
    'pasteLinks': False,
    'pasteImages': False,
    'pasteBlock': [],
    'pasteInline': ['strong', 'b', 'i', 'em'],
    'minHeight': 200,
}
DESCRIPCIONCORTA_REDACTOR_OPTIONS = {
    'buttons': ['bold', 'italic', 'deleted', 'horizontalrule', 'lists',],
    'lang': 'es',
    'pasteLinks': False,
    'pasteImages': False,
    'pasteBlock': [],
    'pasteInline': ['strong', 'b', 'i', 'em'],
    'minHeight': 100,
}

User = settings.AUTH_USER_MODEL

# admin.site.site_header = u'Administración de Videos ' + settings.SITE_NAME
# admin.site.site_title = u'Videos ' + settings.SITE_NAME
# admin.site.index_title = u'Administración'
# admin.site.site_url = None


# class PerfilInline(admin.StackedInline):
#     model = User
#     can_delete = False
#     verbose_name_plural = 'perfiles'

# class UserAdmin(BaseUserAdmin):
#     inlines = (PerfilInline, )

# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)



admin.site.empty_value_display = ''#mark_safe(u'<em>(Vacío)</em>')

class vModelAdmin(admin.ModelAdmin):
    actions_on_top = True

    def get_video_tabs(self, obj=None):
        return None

    class Media:
        css = {
            'all': ('vcms.css',)
        }
        js = ('vcms.js', 'jquery.ellipsis.min.js' )





class ListaInline(admin.TabularInline):
    model = ListaVideo
    suit_classes = 'suit-tab suit-tab-listas'
    fields = ('lista', )
    show_change_link = True
    #fields = ('video', 'player')
    #readonly_fields = ('player', )
    #raw_id_fields = ('video', )
    extra = 1
    verbose_name  = 'lista a la que pertenece este video'
    verbose_name_plural  = 'listas a las que pertenece este video'


class VideoInline(SortableTabularInline):
    model = Video.listas.through
    sortable = 'orden'
    suit_classes = 'suit-tab suit-tab-videos'
    fields = ('video', 'player')
    readonly_fields = ('player', )
    raw_id_fields = ('video', )
    show_change_link = True
    extra = 1
    verbose_name = 'video en esta lista'
    verbose_name_plural  = 'Agregue, reordene o elimine los videos pertenecientes a esta lista'

    def player(self, obj):
        if obj.video:
            if obj.lista.videos.count() < 10:
                t = loader.get_template('vcms/changelist_video_player.html')
                return mark_safe(t.render(Context({'video': obj.video})))
            else:
                t = loader.get_template('vcms/changelist_video_thumbnail.html')
                return mark_safe(t.render(Context({'video': obj.video})))



class VideoChangeForm(ModelForm):
    class Meta:
        model = Video
        exclude = ['pk']
        widgets = {
            'usuario_creacion': TextInput(attrs={'class': 'input-small'}),
            'fecha_creacion': TextInput(attrs={'class': 'input-small'}),
            'archivo_original': TextInput(attrs={
                'data-fp-apikey': 'Ajx8hpwBjSzWFvcASlVIOz',
                'data-fp-button-text': 'Elegir archivo...',
                #'data-fp-mimetype': 'video/*',
                'data-fp-language': 'es',
                #'data-fp-button-class': 'upload_button',
                #'onchange': "alert(event.fpfile.url)",
                'onchange': "$('button[name=_save]).removeAttr('disabled')')",
                'type': "filepicker-dragdrop",
                }),
            'fecha': SuitSplitDateTimeWidget,
            'imagen': AdminImageWidget,
            'sprites': AdminImageWidget,
            'transcripcion': AutosizedTextarea(attrs={'rows': 6,
                                                'class': 'input-block-level'}),
            'resumen': AutosizedTextarea(attrs={'rows': 2,
                                                'class': 'input-block-level'}),
            #'tags': TextInput(attrs={'class': 'input-block-level'}),
            'titulo': TextInput(attrs={'class': 'input-block-level'}),
            'descripcion': RedactorWidget(
                editor_options=DESCRIPCION_REDACTOR_OPTIONS),
            # 'listas': Select2MultipleWidget,
            # 'sitios': CheckboxSelectMultiple,
            'categoria': Select2Widget,
            'pais': Select2Widget,
            'autor': Select2Widget,
            'tipo': Select2Widget({
                'placeholder': 'Elige',
            }),
            #'date_joined': SuitSplitDateTimeWidget,
        }


class VideoAdmin(VersionAdmin, vModelAdmin, AdminImageMixin):
    form = VideoChangeForm
    inlines = [ListaInline]

    list_display = ('padded_pk', 'video', 'info')
    list_filter = ('tipo', 'categoria', 'autor', 'listas', 'estado', 'usuario_creacion',)
    date_hierarchy = 'fecha'
    search_fields = ('titulo', 'descripcion', 'transcripcion', 'observaciones')
    list_select_related = ('autor', 'categoria', 'tipo',)
    
    readonly_fields = ['origen', 'origen_url', 'archivo_original', 'duracion',
                        'procesamiento', 'usuario_creacion', 'fecha_creacion',
                       'usuario_modificacion', 'fecha_modificacion',
                       'archivo']
    readonly_fields_new = []

    info_fields = ('titulo', 'fecha', 'autor', 'descripcion', 'tipo',
                   'categoria', 'duracion_iso', 'usuario_creacion')
    info_fields_procesando = ('origen_url', 'autor', 'duracion_iso',
                              'usuario_creacion', 'fecha_creacion')
    info_fields_error = ('fecha_creacion', 'origen', 'query_procesamiento',
                         'archivo_original', 'observaciones')
    list_per_page = 20

    suit_form_includes = (
        ('vcms/fieldset_video.html', 'top'),
    )

    suit_form_tabs = [
        ('general', u'General'),
        ('editorial', u'Editorial'),
        ('listas', u'Listas'),
        ('seo', 'SEO'),
    ]

    suit_form_tabs_new = [
        ('nuevo', u'Nuevo video'),
    ]

    suit_form_tabs_error = [
        ('nuevo', u'Reintar nuevo video'),
    ]

    # filter_horizontal = ('sitios',)
    radio_fields = {
        'estado': admin.HORIZONTAL,
        'reproduccion': admin.HORIZONTAL,
        'origen': admin.VERTICAL,
    }

    fieldsets_new = [
        (u'Origen del video', {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['origen'],
        }),
        (u'Subir video', {
            'classes': ('suit-tab', 'suit-tab-nuevo', 'local'),
            'fields': ['archivo_original', 'autor'],
        }),
        (u'Importar video', {
            'classes': ('suit-tab', 'suit-tab-nuevo','externo'),
            'fields': ['origen_url'],
        }),
        (mark_safe(u'Destino <small>Elija al menos un sitio a asociar ' \
                   u'con este video. Se puede cambiar después</small>'), {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['sitios'],
        }),
    ]

    fieldsets_procesando = [
        (None, {'classes': ('suit-tab', 'suit-tab-procesando',),
                'fields': [ ],
        }),
    ]

    fieldsets_error = [
        (u'Origen del video', {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['origen'],
        }),
        (u'Subir video', {
            'classes': ('suit-tab', 'suit-tab-nuevo', 'local'),
            'fields': ['archivo_original', 'autor'],
        }),
        (u'Importar video', {
            'classes': ('suit-tab', 'suit-tab-nuevo','externo'),
            'fields': ['origen_url'],
        }),
        (mark_safe(u'Destino <small>Elija al menos un sitio a asociar ' \
                   u'con este video. Se puede cambiar después</small>'), {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['sitios'],
        }),
    ]

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general', 'compact-fieldset'),
            'fields': [('procesamiento', 'duracion'),
                       ('fecha_creacion', 'usuario_creacion',),
                       ('fecha_modificacion', 'usuario_modificacion'),
                       ('origen', 'origen_url')]
        }),

        (u'Archivos', {
            'classes': ('suit-tab', 'suit-tab-general', 'compact-fieldset'),
            'fields': [('imagen', 'sprites'), 'archivo'],
        }),
        
        (u'Básico', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ['fecha', 'autor', 'sitios'],
        }),
        (u'Clasificación', {
            'classes': ('suit-tab', 'suit-tab-general', 'suit-tab-editorial'),
            'fields': ['tipo', 'categoria'],
        }),
        (u'Texto', {
            'classes': ('suit-tab', 'suit-tab-general', 'suit-tab-editorial'),
            'fields': ['titulo', 'resumen', 'descripcion'],
        }),
        (u'Ubicación', {
            'classes': ('suit-tab', 'suit-tab-general', 'suit-tab-editorial'),
            'fields': ['ciudad', 'pais'],
        }),
        # (u'Listas de reproducción', {
        #     'classes': ('suit-tab', 'suit-tab-listas' ),
        #     'fields': ('listas', ),
        # }),
        # (u'Descripción', {
        #     'classes': ('full-width', 'suit-tab', 'suit-tab-general' ),
        #     'fields': ('descripcion', ),
        # }),
        (u'SEO y Accesibilidad', {
             'classes': ('suit-tab', 'suit-tab-seo'),
             'fields': ['tags', 'transcripcion']
        }),
        (u'Políticas de reproducción', {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ['reproduccion'],
        }),
    ]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.usuario_modificacion = request.user
        else:
            obj.usuario_creacion = request.user
        if obj.is_error:
            # reintentar
            obj.procesamiento = Video.PROCESAMIENTO.nuevo
        obj.save()


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, ListaVideo):
                if not instance.orden:
                    max_orden = ListaVideo.objects.all() \
                                    .filter(lista=instance.lista) \
                                    .aggregate(Max('orden'))
                    instance.orden = (max_orden['orden__max'] or 0) + 1
            instance.save()
        formset.save_m2m()

    @property
    def player(self, obj):
        if obj.video:
            t = loader.get_template('vcms/changeform_video_player.html')
            return mark_safe(t.render(Context({'video': obj.video})))


    '''
    Suit row attrs
    '''
    def suit_row_attributes(self, obj, request):
        return { 'class': 'estado-%s' % obj.ESTADO }

    def suit_row_attributes(self, obj, request):
        return {
            'class': '{0}-row'.format(obj.procesamiento),
            'data-video': obj.pk
        }


    def publicado(self, obj):
        return obj.estado == Video.ESTADO.publicado
    publicado.boolean = True


    def info(self, obj):
        if obj.procesamiento == 'error':
            field_names = self.info_fields_error
        elif obj.procesamiento == 'procesando':
            field_names = self.info_fields_procesando
        else:
            field_names = self.info_fields

        fields = []
        for field_name in field_names:
            field = {'value': getattr(obj, field_name)}
            try:
                field['field'] = Video._meta.get_field(field_name)
            except FieldDoesNotExist:
                field['field'] = field_name
                if field_name == 'query_procesamiento':
                    field['value'] = json \
                        .dumps(obj.query_procesamiento, indent=4) \
                        .replace('{', '', ) \
                        .replace('}', '').strip() \
                        .replace("\n", '<br>')
                    field['field'] = 'Procesamiento'
            fields.append(field)

#        if obj.proce
        t = loader.get_template('vcms/changelist_video_info.html')
        html = t.render(Context({'info_fields': fields, 'video': obj}))
        return mark_safe(html)
    info.short_description = u'información'

    def padded_pk(self, obj):
        return  "%05d" % obj.pk
    padded_pk.short_description = 'ID'


    def video(self, obj):
        t = loader.get_template('vcms/changelist_video_player.html')
        return mark_safe(t.render(Context({'video': obj})))
        # return mark_safe('<video height="100" poster="%s" src="%s" />' % (imagen_url, obj.archivo.url))


    def get_video_tabs(self, obj=None):
        if not obj:
            return self.suit_form_tabs_new
        elif obj.is_error:
            return self.suit_form_tabs_error
        else:
            return self.suit_form_tabs

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if not obj or obj.is_error:
            return self.readonly_fields_new
        else:
            return self.readonly_fields
            

    def get_fieldsets(self, request, obj=None):
        if not obj or obj.is_error:
            return self.fieldsets_new
        elif obj.is_procesando:
            return self.fieldsets_procesando
        else:
            return self.fieldsets

    class Media:
        js = ('agregar-video-admin.js',
              '//content.jwplatform.com/libraries/eQkjoc7U.js',
              '//api.filestackapi.com/filestack.js')

admin.site.register(Video, VideoAdmin)

class ListaPlataformaFilter(admin.SimpleListFilter):
    title = 'Plataforma'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'plataforma'

    def lookups(self, request, model_admin):
        return (
            ('wev', 'Sitio web'),
            ('movil', 'Apps móviles'),
            ('tv', 'Apps de TV'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'web':
            return queryset.filter(usar_web=True)
        if self.value() == 'movil':
            return queryset.filter(usar_movil=True)
        if self.value() == 'tv':
            return queryset.filter(usar_tv=True)

class ListaCategoriaFilter(admin.SimpleListFilter):
    title = 'Sección'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'seccion'

    def lookups(self, request, model_admin):
        return [
            ('home', 'Home/Principal')
        ] + [(cat.id, cat.nombre) for cat in Categoria.objects.all()]

    def queryset(self, request, queryset):
        if self.value() == 'home':
            return queryset.filter(categoria__isnull=self.value())
        else:
            return queryset.filter(categoria__pk=self.value())


class ListaChangeForm(ModelForm, vModelAdmin):
    class Meta:
        model = Lista
        exclude = ['pk']
        widgets = {
            'descripcion': RedactorWidget(
                editor_options=DESCRIPCIONCORTA_REDACTOR_OPTIONS),
        }

class ListaAdmin(VersionAdmin, vModelAdmin, SortableModelAdmin):
    form = ListaChangeForm
    inlines = (VideoInline,)
    list_display = ('nombre', 'tipo', 'categoria_', 'videos_', 'player')
    list_filter = ('tipo', ListaCategoriaFilter, ListaPlataformaFilter)
    sortable = 'orden'
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')

    suit_form_tabs = [
        ('general', u'Configuración de la lista'),
        ('videos', u'Videos en la lista'),
    ]
    fieldsets = [
        # (None, {
        #     'classes': ('suit-tab', 'suit-tab-general',),
        #     'fields': ['fecha_creacion', 'fecha_modificacion']
        # }),
        (None, {'classes': ('suit-tab', 'suit-tab-general',),
                'fields': ['tipo',]
        }),
        ('Datos generales', {'classes': ('suit-tab', 'suit-tab-general',),
                'fields': [('nombre', 'usar_nombre', 'usar_descripcion'),
                           'descripcion', 'tags']
        }),
        (u'Categoría', {'classes': ('suit-tab', 'suit-tab-general'),
                'fields': [('categoria')]
        }),
        ('Layout', {'classes': ('suit-tab', 'suit-tab-general'),
                'fields': [('layout')]
        }),
        ('Plataformas', {'classes': ('suit-tab', 'suit-tab-general',
                                     'checkboxes'),
                'fields': [('usar_web', 'usar_movil', 'usar_tv'),
                           ('ads_web', 'ads_movil', 'ads_tv')]
        }),
    ]   

    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        # if obj and getattr(obj, 'nombre', '').startswith('['):
        #     return False
        return True
            

    def categoria_(self, obj):
        if obj.tipo == Lista.TIPO.destacado:
            return obj.categoria or u'Home'
        else:
            return 'N/A'
    categoria_.admin_order_field = 'categoria'

    def videos_(self, obj):
        return obj.enlistado.count()
    videos_.admin_order_field = 'enlistado__count'

    def player(self, obj):
        t = loader.get_template('vcms/changelist_lista_player.html')
        return mark_safe(t.render(Context({'lista': obj, 'videos': obj.enlistado.all() })))
        # return mark_safe('<video height="100" poster="%s" src="%s" />' % (imagen_url, obj.archivo.url))

    class Media:
        js = ('//content.jwplatform.com/libraries/eQkjoc7U.js',
              '//api.filestackapi.com/filestack.js')


admin.site.register(Lista, ListaAdmin)



class AutorAdmin(VersionAdmin, vModelAdmin, SortableModelAdmin):
    sortable = 'orden'
    list_display = ('nombre', 'reproduccion', )
    radio_fields = { 'reproduccion': admin.HORIZONTAL, }
    save_as = True
admin.site.register(Autor, AutorAdmin)


class CategoriaAdmin(VersionAdmin, vModelAdmin, SortableModelAdmin):
    sortable = 'orden'
    save_as = True
admin.site.register(Categoria, CategoriaAdmin)



class TipoChangeForm(ModelForm):
    class Meta:
        model = Tipo
        exclude = ['pk']
        widgets = {
            'descripcion': RedactorWidget(
                editor_options=RESUMEN_REDACTOR_OPTIONS),
        }


class TipoAdmin(VersionAdmin, vModelAdmin, SortableModelAdmin):
    form = TipoChangeForm
    list_display = ('nombre', 'reproduccion', )
    radio_fields = { 'reproduccion': admin.HORIZONTAL, }
    sortable = 'orden'
    fields = ( ('nombre', 'nombre_plural'), 'descripcion', 'reproduccion')
    save_as = True
admin.site.register(Tipo, TipoAdmin)


class SitioAdmin(VersionAdmin, vModelAdmin, SortableModelAdmin):
    sortable = 'orden'
    list_display = ('nombre', 'url', 'reproduccion', )
    radio_fields = { 'reproduccion': admin.HORIZONTAL, }
    save_as = True
admin.site.register(Sitio, SitioAdmin)
