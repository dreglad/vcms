# -*- coding: utf-8 -*- #
from datetime import datetime
import json

from django.contrib.contenttypes.admin import  GenericTabularInline,  GenericStackedInline

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Max, Lookup
from django.forms import ModelForm, RadioSelect, TextInput, FileInput
from django.forms.widgets import CheckboxSelectMultiple
from django.template import loader, Context
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from locality.models import Country, Territory

from django_select2.forms import Select2MultipleWidget

from django_select2.forms import ModelSelect2Widget, Select2Widget, Select2TagWidget

from reversion.admin import VersionAdmin
from salmonella.admin import SalmonellaMixin
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import (
    delete as delete_thumbnail, ImageField, get_thumbnail)
from suit.admin import SortableModelAdmin, SortableTabularInline
from mptt.admin import MPTTModelAdmin

from suit.widgets import SuitSplitDateTimeWidget, SuitDateWidget, AutosizedTextarea
from suit_redactor.widgets import RedactorWidget

from .forms import FilestackWidget, AdminImageWidget
from .models import *

from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.utils.encoding import smart_unicode
from django.utils.html import escape


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
admin.site.empty_value_display = ''#mark_safe(u'<em>(Vacío)</em>')


DEFAULT_FORMFIELD_OVERRIDES = {
    models.ManyToManyField: {
        'widget': Select2MultipleWidget(
            attrs={'data-placeholder': 'Ninguno',
                   'data-minimum-results-for-search': 10}
        )
    },
    models.ForeignKey: {
        'widget': Select2Widget(
            attrs={'data-placeholder': 'Ninguno',
                   'data-minimum-results-for-search': 10}
        )
    },
    ImageField: {
        'widget': AdminImageWidget
    },
    # models.DateTimeField: {
    #     'widget': SuitSplitDateTimeWidget
    # },
    # models.DateTimeField: {
    #     'widget': SuitSplitDateTimeWidget
    # },
    models.DateField: {
        'widget': SuitDateWidget
    }
}


class AutorImageMixin(object):
    def autor(self, obj):
        if obj.autor:
            return mark_safe('<strong>%s</strong>' % obj.autor)


class SortedWithMixin(SortableModelAdmin):
    """
    Only sortable with 'sorted_with'
    """

    def is_sortable(self, request):
        return request.GET.get(self.sorted_with_filter) is not None \
                and len(request.GET.items()) == 1

    def get_list_display(self, request):
        list_display = super(SortedWithMixin, self).get_list_display(
            request)
        if not self.is_sortable(request) and self.sortable in list_display:
             list_display.remove(self.sortable)
        elif self.sorted_with_filter in list_display:
            list_display.remove(self.sorted_with_filter)
        return list_display

    def get_changelist_form(self, request, **kwargs):
        if self.is_sortable(request):
            return super(SortedWithMixin, self) \
                        .get_changelist_form(request, **kwargs)
        else:
            return super(SortableModelAdmin, self) \
                        .get_changelist_form(request, **kwargs)


    def save_model(self, request, obj, form, change):
        if not obj.pk or getattr(obj, self.sortable, None) is None or self.sorted_with in form.changed_data:
            max_order = obj.__class__.objects.filter(
                **{self.sorted_with: getattr(obj, self.sorted_with)}
                ).aggregate(models.Max(self.sortable))
            try:
                next_order = max_order['%s__max' % self.sortable] + 1
            except TypeError:
                next_order = 1
            setattr(obj, self.sortable, next_order)
        super(SortableModelAdmin, self).save_model(request, obj, form, change)


class ModelAdminBase(admin.ModelAdmin):
    actions_on_top = True
    formfield_overrides = DEFAULT_FORMFIELD_OVERRIDES

    def lookup_allowed(self, key, val):
        return True

    def get_video_tabs(self, obj=None):
        return None

    class Media:
        css = {
            'all': ('vcms.css',)
        }
        js = ('vcms.js', 'jquery.ellipsis.min.js' )



class LinkInline(admin.StackedInline):
    model = Link
    suit_classes = 'suit-tab suit-tab-links'
    #fields = ('link',)
    show_change_link = True
    extra = 1
    verbose_name  = 'Link externo'
    verbose_name_plural  = 'Links externos'


class LinkEnListaInline(LinkInline):
    model = Lista.links.through

class LinkEnVideoInline(LinkInline):
    model = Video.links.through

# class VideoInlineBase(admin.TabularInline):
#     suit_classes = 'suit-tab suit-tab-videos'
#     list_fields = ('video', 'player')
#     readonly_fields = ('player',)
#     raw_id_fields = ('video', )
#     show_change_link = True
#     extra = 1
#     lista_field = 'lista'
#
#     def player(self, obj):
#         return
#         if obj.video:
#             if getattr(obj, self.lista_field).videos.count() < 10:
#                 t = loader.get_template('vcms/changelist_video_player.html')
#                 return mark_safe(t.render(Context({'video': obj.video})))
#             else:
#                 t = loader.get_template('vcms/changelist_video_thumbnail.html')
#                 return mark_safe(t.render(Context({'video': obj.video})))

class PaisWidget(ModelSelect2Widget):
    model = Country
    search_fields = [
        'name__icontains'
    ]

    def label_from_instance(self, obj):
        return force_text(obj.name)


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
            #'tags': Select2TagWidget,
            'sprites': AdminImageWidget,
            'transcripcion': AutosizedTextarea(attrs={
                'rows': 6, 'class': 'input-block-level'}),
            'resumen': AutosizedTextarea(attrs={
                'rows': 2, 'class': 'input-block-level'}),
            #'tags': TextInput(attrs={'class': 'input-block-level'}),
            'titulo': TextInput(attrs={'class': 'input-block-level'}),
            'descripcion': RedactorWidget(
                editor_options=DESCRIPCION_REDACTOR_OPTIONS),
            # 'listas': Select2MultipleWidget(attrs={'data-placeholder': 'Ninguna lista', 'data-minimum-results-for-search': 10}),
            'pais': Select2Widget(attrs={'data-placeholder': 'Ninguno', 'data-minimumResultsForSearch': 10}),
            'territorio': Select2Widget(attrs={'data-placeholder': 'Ninguno', 'data-minimum-results-for-search': 10}),
        }


class VideoAdmin(VersionAdmin, ModelAdminBase, AdminImageMixin):
    form = VideoChangeForm
    inlines = [LinkEnVideoInline]

    list_display = ('padded_pk', 'video', 'info')
    list_filter = (
        ('listas', admin.RelatedOnlyFieldListFilter),
        ('listas__clasificador'),
        ('territorio', admin.RelatedOnlyFieldListFilter),
    )
    date_hierarchy = 'fecha'
    search_fields = ('titulo', 'descripcion', 'transcripcion', 'observaciones')
    #list_select_related = ('listas',)

    readonly_fields = ['origen', 'origen_url', 'archivo_original', 'duracion',
                       'procesamiento', 'usuario_creacion', 'fecha_creacion',
                       'usuario_modificacion', 'fecha_modificacion',
                       'archivo']
    readonly_fields_new = []

    info_fields = ( 'fecha', 'titulo', 'descripcion', 'duracion_iso',
                    'pais', 'territorio', 'ciudad')
    info_fields_procesando = ('origen_url', 'duracion_iso',
                              'fecha_creacion')
    info_fields_error = ('fecha_creacion', 'origen', 'procesamiento_status',
                         'archivo_original', 'observaciones')
    list_per_page = 20

    suit_form_includes = (
        ('vcms/fieldset_video.html', 'top'),
    )

    suit_form_tabs = [
        ('general', u'Hoja de datos'),
        ('editorial', u'Redacción'),
        ('clasificacion', u'Clasificación'),
        ('links', u'Links'),
        ('seo', 'SEO'),
    ]

    suit_form_tabs_new = [
        ('nuevo', u'Nuevo video'),
    ]

    suit_form_tabs_error = [
        ('nuevo', u'Reintar nuevo video'),
    ]

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
            'fields': ['archivo_original', ],
        }),
        (u'Importar video', {
            'classes': ('suit-tab', 'suit-tab-nuevo','externo'),
            'fields': ['origen_url'],
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
            'fields': ['archivo_original', ],
        }),
        (u'Importar video', {
            'classes': ('suit-tab', 'suit-tab-nuevo','externo'),
            'fields': ['origen_url'],
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

        # (u'Básico', {
        #     'classes': ('suit-tab', 'suit-tab-general'),
        #     'fields': ['fecha', 'serie', 'autor',],
        # }),
        (u'Clasificación', {
            'classes': ('suit-tab', 'suit-tab-clasificacion'),
            'fields': ['listas',]
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-editorial'),
            'fields': ['titulo', 'descripcion'],
        }),
        (u'Links', {
            'classes': ('suit-tab', 'suit-tab-links'),
            'fields': ['links', ],
        }),
        (u'Ubicación', {
            'classes': ('suit-tab', 'suit-tab-editorial'),
            'fields': ['fecha', 'pais', 'territorio', 'ciudad'],
        }),
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


    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)
    #     for obj in formset.deleted_objects:
    #         obj.delete()
    #     for instance in instances:
    #         if isinstance(instance, DestacadoVideo):
    #             if not instance.orden:
    #                 max_orden = DestacadoVideo.objects.all() \
    #                                 .filter(destacado=instance.destacado) \
    #                                 .aggregate(Max('orden'))
    #                 instance.orden = (max_orden['orden__max'] or 0) + 1
    #         instance.save()
    #     formset.save_m2m()

    # fields = ('video', 'pagina', 'player', 'orden')

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
                if field_name == 'procesamiento_status':
                    field['value'] = json \
                        .dumps(obj.procesamiento_status, indent=4) \
                        .replace('{', '', ) \
                        .replace('}', '').strip() \
                        .replace("\n", '<br>')
                    field['field'] = 'Procesamiento'
            fields.append(field)


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


class LinkAdmin(VersionAdmin, ModelAdminBase):
    list_display = ('url', 'titulo', 'tipo', 'videos_')
    list_filter = ('tipo', 'tipo',)
    search_fields = ['titulo', 'url']
    # readonly_fields = ('videos_',)
    fieldsets= [
        (u'Datos del link', {
            'classes': ('suit-tab-general'),
            'fields': [('url', 'blank'), 'titulo', 'tipo']
        })
    ]

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'



class PlataformaAdmin(VersionAdmin, ModelAdminBase, SortableModelAdmin):
    list_display = ('nombre', 'tipo', 'usar_publicidad', 'api_key')
    list_filter = ('tipo', 'usar_publicidad',)
    sortable = 'orden'


# class AutorAdmin(VersionAdmin, ModelAdminBase, SortableModelAdmin, AdminImageMixin):
#     sortable = 'orden'
#     list_display = ('nombre', 'logo_', 'url', 'reproduccion')
#     radio_fields = { 'reproduccion': admin.HORIZONTAL, }
#     save_as = True
#
#     def logo_(self, obj):
#         if obj.logo:
#             return mark_safe(u'<img style="max-width: 300px; max-height: 150px;" src="%s"' % obj.logo.url)
#
#
# class CategoriaSerieInline(admin.TabularInline):
#     model = Serie
#     extra = 0
#     fields = ('nombre',)
#
# class CategoriaDestacadoInline(admin.TabularInline):
#     model = Destacado
#     extra = 0
#     fields = ('nombre',)
#
# class CategoriaAdmin(VersionAdmin, ModelAdminBase, SortableModelAdmin):
#     inlines = [DestacadoAdminGen]
#     list_display = ('nombre',)
#     sortable = 'orden'
#     save_as = True

#
#
# class TipoChangeForm(ModelForm):
#     class Meta:
#         model = Tipo
#         exclude = ['pk']
#         widgets = {
#             'descripcion': RedactorWidget(
#                 editor_options=RESUMEN_REDACTOR_OPTIONS),
#         }
#
#
# class TipoAdmin(VersionAdmin, ModelAdminBase, SortableModelAdmin):
#     form = TipoChangeForm
#     list_display = ('nombre', 'reproduccion', )
#     radio_fields = { 'reproduccion': admin.HORIZONTAL, }
#     sortable = 'orden'
#     fields = ( ('nombre', 'nombre_plural'), 'descripcion', 'reproduccion')
#     save_as = True



class ListaInline(SortableTabularInline):
    model = ListaEnPagina
    sortable = 'orden'
    suit_classes = 'suit-tab suit-tab-listas'
    show_change_link = True
    #list_fields = ('id',)
    raw_id_fields = ('lista',)
    #salmonella_fields = ('lista',)
    fields = (
        'lista', 'pagina', 'nombre', 'mostrar_nombre', 'mostrar_descripcion',
        'mostrar_paginacion', 'num_videos', 'layout', 'invertido', 'junto', 'orden'
    )
    extra = 0
    verbose_name  = 'Lista'
    verbose_name_plural  = 'Listas'

class VideoInline(SortableTabularInline):
    model = VideoEnPagina
    sortable = 'orden'
    suit_classes = 'suit-tab suit-tab-videos'
    show_change_link = True
    list_fields = ('video', 'player', 'orden')
    raw_id_fields = ('video',)
    readonly_fields = ('player',)
    #salmonella_fields = ('lista',)
    fields = ('video', 'pagina', 'player', 'orden',)
    extra = 0
    verbose_name  = 'video destacado'
    verbose_name_plural  = 'videos destacados'

    def player(self, obj):
        if obj.video:
            t = loader.get_template('vcms/changelist_video_thumbnail.html')
            return mark_safe(t.render(Context({'video': obj.video})))

    def save_model(self, request, obj, form, change):
        if not obj.pk or getattr(obj, self.sortable, None) is None or self.sorted_with in form.changed_data:
            max_order = obj.__class__.objects.filter(
                **{self.sorted_with: getattr(obj, self.sorted_with)}
                ).aggregate(models.Max(self.sortable))
            try:
                next_order = max_order['%s__max' % self.sortable] + 1
            except TypeError:
                next_order = 1
            setattr(obj, self.sortable, next_order)
        super(SortableModelAdmin, self).save_model(request, obj, form, change)


    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     if db_field.name in ('lista',):
    #         kwargs.pop('request', None)
    #         kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
    #         return db_field.formfield(**kwargs)
    #     return super(ListaInline,self).formfield_for_dbfield(db_field,**kwargs)



    class ClasificadorFilter(admin.SimpleListFilter):
        title = 'Clasificador'
        parameter_name = 'clasificador'

        def lookups(self, request, model_admin):
            return [
                ('home', 'Principal')
            ] + [(cat.id, cat.nombre) for cat in Categoria.objects.all()]

        def queryset(self, request, queryset):
            if self.value() == 'home':
                return queryset.filter(categoria__isnull=self.value())
            elif self.value() is not None:
                return queryset.filter(clasificador__slug=self.value())
            else:
                return queryset


class PaginaAdmin(MPTTModelAdmin, ModelAdminBase, SortableModelAdmin):
    inlines = [VideoInline, ListaInline]
    mptt_level_indent = 20
    list_display = (
        'titulo', 'mostrar_titulo', 'mostrar_descripcion', 'mostrar_en_menu',
        'invertido', 'junto', 'listas_', 'videos_', 'activo')
    list_filter = (
        ('listas', admin.RelatedOnlyFieldListFilter),
    )
    list_editable = ('activo',)
    sortable = 'orden'
    suit_form_tabs = [
        ('general', u'General'),
        ('videos', u'1. Videos destacados'),
        ('listas', u'2. Listas embedidas'),
        # ('links', u'Links'),
        ('seo', 'SEO'),
    ]

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': [
                ('parent', 'mostrar_en_menu'),
                ('titulo', 'mostrar_titulo', 'mostrar_descripcion'),
                'descripcion'
            ],
        }),
        (u'Visualización', {
            'classes': ('suit-tab', 'suit-tab-videos',),
            'fields': [ ('invertido', 'junto')],
        }),
        (u'SEO y Accesibilidad', {
             'classes': ('suit-tab', 'suit-tab-seo'),
             'fields': ['descripcion',]
        }),
    ]

    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs

    def listas_(self, obj):
        return obj.listas.count()
    listas_.admin_order_field = 'listas__count'

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'



class FiltroAdmin(ModelAdminBase):
    pass

class ListaAdmin(ModelAdminBase):
    inlines = [LinkEnListaInline]
    list_display = ('nombre', 'activo', 'videos_', 'clasificador')
    list_filter = ('clasificador',)
    list_editable = ('activo',)
    search_fields = ['nombre', 'clasificador__nombre']
    list_per_page = 100

    suit_form_tabs = (
        ('general', 'General'),
        ('relacionadas', 'Listas relacionadas'),
        ('media', 'Medios'),
        ('links', 'Links'),
        ('seo', 'SEO y Accesibilidad'),

    )
    fieldsets= [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ['clasificador', ('nombre', 'nombre_plural'), 'descripcion'],
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-media'),
            'fields': [
                ('icono', 'mostrar_icono'), ('imagen', 'mostrar_imagen'),
                ('cortinilla_inicio', 'mostrar_cortinilla_inicio'),
                ('cortinilla_final', 'mostrar_cortinilla_final'),
            ],
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-relacionadas'),
            'fields': ['listas_relacionadas'],
        }),
        (u'Link interno', {
            'classes': ('suit-tab', 'suit-tab-links'),
            'fields': ['pagina', ],
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-seo'),
            'fields': ['tags'],
        }),
    ]

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'

    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs


class ClasificadorAdmin(ModelAdminBase):
    list_display = ('nombre', 'nombre_plural', 'listas_', 'videos_')
    # suit_form_tabs = (
    #     ('general', 'General'),
    # )
    fieldsets= [
        ('Datos del clasificador', {
            'classes': ('suit-tab-general'),
            'fields': [('nombre', 'nombre_plural'), 'descripcion'],
        }),
    ]

    def videos_(self, obj):
        return Video.objects.filter(listas__clasificador=obj).count()
    videos_.admin_order_field = 'videos__count'

    def listas_(self, obj):
        return obj.listas.count()
    listas_.admin_order_field = 'listas__count'




admin.site.register(Video, VideoAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Plataforma, PlataformaAdmin)
admin.site.register(Lista, ListaAdmin)
admin.site.register(Clasificador, ClasificadorAdmin)
admin.site.register(Pagina, PaginaAdmin)
admin.site.register(Filtro, FiltroAdmin)
