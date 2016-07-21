# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from datetime import datetime
import json

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.forms import ModelForm, TextInput
from django.template import loader, Context
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from django_select2.forms import Select2MultipleWidget
from django_select2.forms import ModelSelect2Widget, Select2Widget, Select2TagWidget
from locality.models import Country, Territory
from mptt.admin import MPTTModelAdmin
from reversion.admin import VersionAdmin
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import ImageField, get_thumbnail
from sorl.thumbnail.templatetags.thumbnail import margin
from suit.admin import SortableModelAdmin, SortableStackedInline
from suit.widgets import SuitSplitDateTimeWidget, SuitDateWidget, AutosizedTextarea
from suit_redactor.widgets import RedactorWidget

from .forms import FilestackWidget, AdminImageWidget
from .models import *


admin.site.empty_value_display = ''


REDACTOR_OPTIONS_LG = {
    'buttons': ['bold', 'italic', 'deleted', 'horizontalrule', 'lists',],
    'lang': settings.LANGUAGE_CODE,
    'pasteLinks': False,
    'pasteImages': False,
    'pasteBlock': [],
    'pasteInline': ['strong', 'b', 'i', 'em'],
    'minHeight': 320,
}

REDACTOR_OPTIONS_SM = {
    'buttons': ['bold', 'italic', 'deleted', 'horizontalrule', 'lists',],
    'lang': settings.LANGUAGE_CODE,
    'pasteLinks': False,
    'pasteImages': False,
    'pasteBlock': [],
    'pasteInline': ['strong', 'b', 'i', 'em'],
    'minHeight': 75,
}

DEFAULT_FORMFIELD_OVERRIDES = {
    models.ManyToManyField: {
        'widget': Select2MultipleWidget(
            attrs={'data-placeholder': 'Ninguno',
                   'data-minimum-results-for-search': 10})
    },
    models.ForeignKey: {
        'widget': Select2Widget(
            attrs={'data-placeholder': 'Ninguno',
                   'data-minimum-results-for-search': 10})
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

DISPLAYABLE_FIELDSET = (
    _('Visualización'), {
    'classes': ('suit-tab', 'suit-tab-display'),
    'fields': [
        ('mostrar_nombre', 'mostrar_maximo'),
        ('mostrar_descripcion', 'mostrar_paginacion'),
        ('layout', 'margen'),
        ('mostrar_publicidad', 'tema'),
    ],
})


class AutorImageMixin(object):
    def autor(self, obj):
        if obj.autor:
            return mark_safe('<strong>%s</strong>' % obj.autor)


class SortedWithMixin(SortableModelAdmin):
    radio_fields = {
        'mostrar_nombre': admin.HORIZONTAL,
        'mostrar_descripcion': admin.HORIZONTAL,
        'mostrar_paginacion': admin.HORIZONTAL,
    }

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

    def formfield_for_dbfield(self, db_field, **kwargs):
        if not 'widget' in kwargs:
            if db_field.name in ('descripcion'):
                 kwargs['widget'] = RedactorWidget(
                    editor_options=REDACTOR_OPTIONS_SM)
            elif db_field.name in ('meta_descripcion',):
                 kwargs['widget'] = AutosizedTextarea(
                    attrs={'rows': 3, 'class': 'input-block-level'})
            elif db_field.name in ('tags',):
                 kwargs['widget'] = Select2TagWidget(
                    attrs={'data-token-separators': '[","]'})
        return super(ModelAdminBase, self).formfield_for_dbfield(db_field,
                                                                 **kwargs)


class LinkInline(admin.StackedInline):
    model = Link
    suit_classes = 'suit-tab suit-tab-links'
    show_change_link = True
    extra = 1
    verbose_name = _('Link externo')
    verbose_name_plural = _('Links externos')


class LinkEnListaInline(LinkInline):
    model = Lista.links.through


class LinkEnVideoInline(LinkInline):
    model = Video.links.through


class PaisWidget(ModelSelect2Widget):
    model = Country
    search_fields = ('name__icontains',)

    def label_from_instance(self, obj):
        return force_text(obj.name)


class VideoChangeForm(ModelForm):
    class Meta:
        model = Video
        exclude = ['pk']
        widgets = {
            'archivo_original': TextInput(attrs={
                'data-fp-apikey': 'Ajx8hpwBjSzWFvcASlVIOz',
                'data-fp-button-text': 'Elegir archivo...',
                'data-fp-language': 'es', 'type': 'filepicker-dragdrop',
                'onchange': '$("button[name=_save]").removeAttr("disabled")'}),
            'descripcion': RedactorWidget(editor_options=REDACTOR_OPTIONS_LG),
            'fecha_creacion': TextInput(attrs={'class': 'input-small'}),
            'metadescripcion': AutosizedTextarea(
                attrs={'rows': 6, 'class': 'input-block-level'}),
            'pais': Select2Widget(attrs={'data-placeholder': 'Ninguno',
                                         'data-minimumResultsForSearch': 10}),
            'resumen': AutosizedTextarea(
                attrs={'class': 'input-block-level', 'rows': 2}),
            'sprites': AdminImageWidget,
            'tags': Select2TagWidget(attrs={'data-token-separators': '[","]'}),
            'territorio': Select2Widget(
                attrs={'data-placeholder': 'Ninguno',
                       'data-minimum-results-for-search': 10}),
            'titulo': TextInput(attrs={'class': 'input-block-level'}),
            'usuario_creacion': TextInput(attrs={'class': 'input-small'}),
        }


class VideoAdmin(VersionAdmin, ModelAdminBase, AdminImageMixin):
    form = VideoChangeForm
    inlines = [LinkEnVideoInline]
    list_per_page = 20
    list_display = ('padded_pk', 'video', 'info')
    list_filter = (('listas', admin.RelatedOnlyFieldListFilter), 'estado')
    search_fields = ('titulo', 'descripcion', 'meta_descripcion', 'observaciones')
    date_hierarchy = 'fecha'
    readonly_fields = [
        'origen', 'origen_url', 'archivo_original', 'duracion', 'procesamiento',
        'usuario_creacion', 'fecha_creacion', 'usuario_modificacion',
        'fecha_modificacion', 'archivo', 'resolucion', 'max_resolucion',
    ]
    readonly_fields_new = []
    info_fields = (
        'fecha', 'titulo', 'descripcion', 'estado', 'duracion_iso', 'pais',
        'territorio', 'ciudad', 'listas', 'tags'
    )
    info_fields_procesando = (
        'origen_url', 'duracion_iso', 'fecha_creacion'
    )
    info_fields_error = (
        'fecha_creacion', 'origen', 'procesamiento_status', 'archivo_original',
        'observaciones'
    )
    suit_form_includes = (
        ('vcms/fieldset_video.html', 'top'),
    )
    suit_form_tabs = [
        ('general', _('General')),
        ('clasificacion', _('Clasificación')),
        ('seo', _('SEO')),
    ]
    suit_form_tabs_new = [
        ('nuevo', _('Nuevo video')),
    ]
    suit_form_tabs_error = [
        ('nuevo', _('Reintar nuevo video')),
    ]
    radio_fields = {
        'estado': admin.HORIZONTAL,
        'reproduccion': admin.HORIZONTAL,
        'origen': admin.VERTICAL,
    }
    fieldsets_new = [
        (_('Origen del video'), {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['origen'],
        }),
        (_('Subir video'), {
            'classes': ('suit-tab', 'suit-tab-nuevo', 'local'),
            'fields': ['archivo_original', ],
        }),
        (_('Importar video'), {
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
        (_('Origen del video'), {
            'classes': ('suit-tab', 'suit-tab-nuevo'),
            'fields': ['origen'],
        }),
        (_('Subir video'), {
            'classes': ('suit-tab', 'suit-tab-nuevo', 'local'),
            'fields': ['archivo_original', ],
        }),
        (_('Importar video'), {
            'classes': ('suit-tab', 'suit-tab-nuevo','externo'),
            'fields': ['origen_url'],
        }),
    ]
    fieldsets = [
        ('Ficha de datos', {
            'classes': ('suit-tab', 'suit-tab-general', 'compact-fieldset'),
            'fields': [
                ('procesamiento', 'duracion'),
                ('fecha_creacion', 'usuario_creacion',),
                ('fecha_modificacion', 'usuario_modificacion'),
                ('origen', 'origen_url'),
                ('resolucion', 'max_resolucion')
            ]
        }),
        (_('Archivos'), {
            'classes': ('suit-tab', 'suit-tab-general', 'compact-fieldset'),
            'fields': [('imagen', 'sprites'), 'archivo_original'],
        }),
        (_('Listas'), {
            'classes': ('suit-tab', 'suit-tab-clasificacion'),
            'fields': ['listas',]
        }),
        (_('Redacción'), {
            'classes': ('suit-tab', 'suit-tab-clasificacion'),
            'fields': ['titulo', 'descripcion', 'links'],
        }),
        (_('Ubicación'), {
            'classes': ('suit-tab', 'suit-tab-clasificacion'),
            'fields': ['pais', 'territorio', 'ciudad'],
        }),
        (_('Fecha'), {
            'classes': ('suit-tab', 'suit-tab-clasificacion'),
            'fields': ['fecha',]
        }),
        (_('SEO'), {
            'classes': ('suit-tab', 'suit-tab-seo'),
            'fields': [
                'tags', 'meta_descripcion', 'reproduccion', 'custom_metadata'
            ]
        }),
    ]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.usuario_modificacion = request.user
        else:
            obj.usuario_creacion = request.user
        if obj.procesamiento == obj.PROCESAMIENTO.error:
            obj.procesamiento = Video.PROCESAMIENTO.nuevo  # retry
        obj.save()

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('descripcion',):
             kwargs['widget'] = RedactorWidget(editor_options=REDACTOR_OPTIONS_LG)
        return super(VideoAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_queryset(self, request):
        return super(VideoAdmin, self).get_queryset(request) \
                                      .prefetch_related('listas', 'tags')

    def player(self, obj):
        if obj.video:
            t = loader.get_template('vcms/changeform_video_player.html')
            return mark_safe(t.render(Context({'video': obj.video})))

    def suit_row_attributes(self, obj, request):
        return { 'class': 'estado-%s' % obj.ESTADO }

    def suit_row_attributes(self, obj, request):
        return { 'class': '{0}-row'.format(obj.procesamiento),
                 'data-video': obj.pk }

    def publicado(self, obj):
        return obj.estado == Video.ESTADO.publicado
    publicado.boolean = True

    def info(self, obj):
        if obj.procesamiento == obj.PROCESAMIENTO.error:
            field_names = self.info_fields_error
        elif obj.procesamiento == obj.PROCESAMIENTO.procesando:
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
    info.short_description = _('información')

    def padded_pk(self, obj):
        return  "%05d" % obj.pk
    padded_pk.short_description = 'ID'

    def video(self, obj):
        t = loader.get_template('vcms/changelist_video_player.html')
        return mark_safe(t.render(Context({'video': obj})))

    def get_video_tabs(self, obj=None):
        if not obj:
            return self.suit_form_tabs_new
        elif obj.procesamiento == obj.PROCESAMIENTO.error:
            return self.suit_form_tabs_error
        else:
            return self.suit_form_tabs

    def get_readonly_fields(self, request, obj=None):
        if not obj or obj.procesamiento == obj.PROCESAMIENTO.error:
            return self.readonly_fields_new
        else:
            return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj or obj.procesamiento == obj.PROCESAMIENTO.error:
            return self.fieldsets_new
        elif obj.procesamiento == obj.PROCESAMIENTO.procesando:
            return self.fieldsets_procesando
        else:
            return self.fieldsets

    class Media:
        js = ('agregar-video-admin.js', 
              '//content.jwplatform.com/libraries/eQkjoc7U.js',
              '//api.filestackapi.com/filestack.js')


class LinkAdmin(VersionAdmin, ModelAdminBase):
    list_display = ('url', 'titulo', 'tipo', 'videos_')
    list_filter = ('tipo', 'tipo')
    search_fields = ['titulo', 'url']
    fieldsets = [
        (_('Datos del link'), {
            'classes': ('suit-tab-general', ),
            'fields': [('url', 'blank'), 'titulo', 'tipo']
        })
    ]

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'


class PlataformaAdmin(ModelAdminBase, SortableModelAdmin):
    list_display = ('nombre', 'descripcion', 'tipo', 'api_key')
    list_filter = ('tipo', 'mostrar_publicidad')
    sortable = 'orden'
    suit_form_tabs = [
        ('general', _('General')),
        ('display', _('Configuración global de visualización')),
        ('seo', _('SEO')),
    ]
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ['nombre', ('tipo', 'link'), 'descripcion'],
        }),
        (_('SEO'), {
             'classes': ('suit-tab', 'suit-tab-seo'),
             'fields': ['tags', 'meta_descripcion',]
        }),
        DISPLAYABLE_FIELDSET,
    ]
    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs


class ListaInline(SortableStackedInline):
    model = ListaEnPagina
    raw_id_fields = ('lista',)
    readonly_fields = ('lista_', 'videos_')
    fields = [
        'orden', 'pagina', 'lista',
        'lista_', 'nombre', 'descripcion', 'videos_',
        ('mostrar_nombre', 'mostrar_maximo'),
        ('mostrar_descripcion', 'mostrar_paginacion'),
        ('layout', 'margen'),
        ('mostrar_publicidad', 'tema'),
    ]
    suit_classes = 'suit-tab suit-tab-display'
    show_change_link = True
    sortable = 'orden'
    verbose_name = _('Lista')
    verbose_name_plural = _('2. Listas de videos')
    extra = 0

    def lista_(self, obj):
        return mark_safe(
            '<div>{nombre} <a class="icon-pencil icon-alpha75"' \
            'href="{lista_url}"> </a> &nbsp; ({clasif})</div>'.format(
                nombre=obj.lista.nombre_plural or obj.lista.nombre,
                clasif=obj.lista.clasificador.nombre,
                lista_url = reverse(
                    'admin:videos_lista_change', args=[obj.lista.pk])))

    def videos_(self, obj):
        videos_url = reverse('admin:videos_video_changelist')
        result = [
            '<div class="thumbnails"><div>Videos totales: ',
            '<a href="{0}?listas__id__exact={1}">{2}</a></div>'.format(
                videos_url, obj.lista.id, obj.lista.videos.publicos().count())
        ]
        for video in obj.lista.videos.publicos()[:20]:
            url = reverse('admin:videos_video_change', args=[video.id])
            result.append('<a class="video" href="{0}" title="{1}">'.format(
                url, video.titulo))
            im = get_thumbnail(video.imagen.file, '64x36', crop='center')           
            result.append('<img src="{0}">').format(im.url)
            result.append('</a>')
        result.append('</div>')
        return mark_safe(''.join(result))

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('descripcion',):
             kwargs['widget'] = RedactorWidget(
                 editor_options=REDACTOR_OPTIONS_SM)
        return super(ListaInline, self).formfield_for_dbfield(
            db_field, **kwargs)


class VideoInline(SortableStackedInline):
    model = VideoEnPagina
    list_fields = ('video', 'video_', 'orden')
    raw_id_fields = ('video',)
    readonly_fields = ('video_',)
    fields = [
        'pagina', 'orden', 'video', (
            'video_', 'mostrar_nombre', 'mostrar_descripcion',
            'mostrar_publicidad', 'margen', 'tema',
            ),
    ]
    show_change_link = True
    suit_classes = 'suit-tab suit-tab-display'
    extra = 0
    sortable = 'orden'
    verbose_name = _('video destacado')
    verbose_name_plural  = _('1. Videos destacados de la página')

    def video_(self, obj):
        if obj.video:
            im = get_thumbnail(obj.video.imagen.file, '242x136', crop='center')
            return mark_safe(
                ('<img src="{url}"><div class="titulo" style="width:242px; '
                 'margin:{margin}">{titulo}</div>').format(
                    titulo=obj.video.titulo, url=im.url,
                    margin=margin(im, '242x136')))

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


class ClasificadorFilter(admin.SimpleListFilter):
    title = _('Clasificador')
    parameter_name = 'clasificador'

    def lookups(self, request, model_admin):
        return [(obj.slug, obj.nombre) for obj in Clasificador.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clasificador__slug=self.value())
        else:
            return queryset


class PaginaAdmin(MPTTModelAdmin, SortableModelAdmin, ModelAdminBase):
    inlines = [VideoInline, ListaInline]
    sortable = 'orden'
    mptt_level_indent = 20
    list_display = (
        'nombre', 'mostrar_en_menu', 'videos_', 'listas_')
    list_filter = (
        ('listas', admin.RelatedOnlyFieldListFilter),
    )
    suit_form_tabs = [
        ('display', _('Página')),
        ('seo', _('SEO')),
    ]
    suit_form_includes = (
        ('admin/paginas/videos_include.html', 'top', 'videos'),
        # ('admin/examples/country/tab_info.html', '', 'info'),
        # ('admin/examples/country/disclaimer.html'),
    )
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-display'),
            'fields': [('nombre', 'mostrar_en_menu'), 'parent', 'descripcion'],
        }),
        (_('SEO'), {
             'classes': ('suit-tab', 'suit-tab-seo'),
             'fields': ['meta_descripcion', 'tags']
        }),
        DISPLAYABLE_FIELDSET,
    ]

    def get_queryset(self, request):
        paginas = super(PaginaAdmin, self).get_queryset(request)
        paginas = paginas.prefetch_related('videos_en_pagina', 'listas', 'tags')
        return paginas

    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs

    def listas_(self, obj):
        return obj.listas.count()
    listas_.admin_order_field = 'listas__count'

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'
    videos_.short_description = _('videos destacados')


class FiltroAdmin(ModelAdminBase):
    pass


class ListaAdmin(ModelAdminBase):
    inlines = [LinkEnListaInline]
    list_per_page = 100
    list_display = ('nombre_', 'icono_', 'clasificador', 'videos_', 'descripcion')
    search_fields = ['nombre', 'clasificador__nombre']
    list_filter = (ClasificadorFilter,)
    suit_form_tabs = (
        ('general', _('General')),
        ('relacionadas', _('Listas relacionadas')),
        ('media', _('Medios')),
        ('links', _('Links')),
        ('seo', _('SEO')),
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
                ('cortinilla_inicial', 'mostrar_cortinilla_inicial'),
                ('cortinilla_final', 'mostrar_cortinilla_final'),
            ],
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-relacionadas'),
            'fields': ['listas_relacionadas'],
        }),
        (_('Link interno'), {
            'classes': ('suit-tab', 'suit-tab-links'),
            'fields': ['pagina', ],
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-seo'),
            'fields': ['tags', 'meta_descripcion'],
        }),
    ]

    def videos_(self, obj):
        return obj.videos.count()
    videos_.admin_order_field = 'videos__count'

    def nombre_(self, obj):
        return obj.nombre_plural or obj.nombre
    nombre_.admin_order_field = _('nombre')

    def icono_(self, obj):
        if obj.icono:
            im = get_thumbnail(obj.icono.file, '30')
            return mark_safe(
                '<img src="{0}" style="margin:{1}">'.format(
                    im.url, margin(im, '35x35')))
    icono_.admin_order_field = 'icono'

    def get_video_tabs(self, obj=None):
        return self.suit_form_tabs


class ClasificadorAdmin(ModelAdminBase):
    list_display = ('nombre', 'nombre_plural', 'listas_', 'videos_')
    suit_form_tabs = (
        ('general', _('General')),
    )
    fieldsets = [
        (_('Datos del clasificador'), {
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


admin.site.register(Clasificador, ClasificadorAdmin)
admin.site.register(Filtro, FiltroAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Lista, ListaAdmin)
admin.site.register(Pagina, PaginaAdmin)
admin.site.register(Plataforma, PlataformaAdmin)
admin.site.register(Video, VideoAdmin)
