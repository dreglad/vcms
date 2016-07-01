# -*- coding: utf-8 -*- #
import json
import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from rest_framework import mixins, routers, serializers, viewsets, filters
from rest_framework.fields import URLField
from sorl.thumbnail import get_thumbnail

from videos.models import *


"""
Fields
"""
class HyperlinkedSorlImageField(serializers.ImageField):

    """A Django REST Framework Field class returning hyperlinked scaled and cached images."""

    def __init__(self, geometry_string, options={}, *args, **kwargs):
        """
        Create an instance of the HyperlinkedSorlImageField image serializer.
        Args:
            geometry_string (str): The size of your cropped image.
            options (Optional[dict]): A dict of sorl options.
            *args: (Optional) Default serializers.ImageField arguments.
            **kwargs: (Optional) Default serializers.ImageField keyword
            arguments.
        For a description of sorl geometry strings and additional sorl options,
        please see https://sorl-thumbnail.readthedocs.org/en/latest/examples.html?highlight=geometry#low-level-api-examples
        """  # NOQA
        self.geometry_string = geometry_string
        self.options = options

        super(HyperlinkedSorlImageField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        """
        Perform the actual serialization.
        Args:
            value: the image to transform
        Returns:
            a url pointing at a scaled and cached image
        """
        if not value:
            return None

        image = get_thumbnail(value, self.geometry_string, **self.options)

        try:
            request = self.context.get('request', None)
            return request.build_absolute_uri(image.url)
        except:
            try:
                return super(HyperlinkedSorlImageField, self).to_representation(image.url)
            except AttributeError:  # NOQA
                return super(HyperlinkedSorlImageField, self).to_native(image.url)  # NOQA
    to_native = to_representation


class TagsField(serializers.CharField):
    def to_representation(self, value):
        tags = [tag.name for tag in value.all()]
        return ','.join(tags)


"""
Serializers
"""

FIELDS_BASE = (
    'id', 'fecha_creacion', 'fecha_modificacion', 'slug',
)
FIELDS_LISTA = FIELDS_BASE + (
    'activo', 'nombre', 'descripcion', 'descripcion_plain', 'fecha_termino',
    'youtube_playlist', 'plataformas', 'tags', 'videos'
)


class PlataformaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Plataforma
        fields = FIELDS_BASE + (
            'tipo', 'nombre', 'descripcion', 'usar_publicidad',
        )

class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Link
        exclude = ('usuario_creacion', 'usuario_modificacion')
        # fields = FIELDS_BASE + (
        #     'nombre', 'logo', 'usar_logo', 'icono', 'url', 'usar_url', 'icono',
        #     'cortinilla_inicio', 'usar_cortinilla_inicio', 'cortinilla_final',
        #     'usar_cortinilla_final',
        # )


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Link
        exclude = ('usuario_creacion', 'usuario_modificacion')
        # fields = FIELDS_BASE + (
        #     'nombre', 'logo', 'usar_logo', 'icono', 'url', 'usar_url', 'icono',
        #     'cortinilla_inicio', 'usar_cortinilla_inicio', 'cortinilla_final',
        #     'usar_cortinilla_final',
        # )

class ListaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lista
        exclude = ('usuario_creacion', 'usuario_modificacion')
        # fields = FIELDS_BASE + (
        #     'nombre', 'logo', 'usar_logo', 'icono', 'url', 'usar_url', 'icono',
        #     'cortinilla_inicio', 'usar_cortinilla_inicio', 'cortinilla_final',
        #     'usar_cortinilla_final',
        # )


class ClasificadorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clasificador
        exclude = ('usuario_creacion', 'usuario_modificacion')
        # fields = FIELDS_BASE + ('nombre',)




class PaginaSerializer(serializers.HyperlinkedModelSerializer):
    # tags = TagsField(read_only=True)
    class Meta:
        model = Pagina
        #exclude = ('usuario_creacion', 'usuario_modificacion')


# class TipoSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Tipo
#         fields = FIELDS_BASE + ('nombre', 'nombre_plural', 'descripcion',
#                                 'descripcion_plain')


# class SerieSerializer(serializers.HyperlinkedModelSerializer):
#     tags = TagsField(read_only=True)
#
#     class Meta:
#         model = Serie
#         fields = FIELDS_LISTA + ('imagen', 'autor', 'categoria',)


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagsField(read_only=True)
    thumbnail_100 = HyperlinkedSorlImageField('100', source='imagen',
                                              read_only=True)
    thumbnail_250 = HyperlinkedSorlImageField('250', source='imagen',
                                              read_only=True)
    thumbnail_500 = HyperlinkedSorlImageField('500', source='imagen',
                                              read_only=True)
    thumbnail_1000 = HyperlinkedSorlImageField('1000', source='imagen',
                                               read_only=True)
    url = URLField(source='get_absolute_url')

    class Meta:
        model = Video
        fields = FIELDS_BASE + ('estado', 'procesamiento', 'slug', 'fecha',
            'url', 'origen', 'origen_url', 'youtube_id', 'duracion',
            'original_width', 'original_height', 'resolucion', 'hls', 'archivo',
            'sprites', 'captions', 'imagen', 'thumbnail_100', 'thumbnail_250',
            'thumbnail_500', 'thumbnail_1000', 'titulo', 'resumen',
            'descripcion', 'descripcion_plain', 'transcripcion',
            'links', 'listas', 'dash', 'captions', 'paginas',
            'tags', 'observaciones')


"""
Viewsets
"""
# class AutorViewSet(ViewSetBase):
#     queryset = Autor.objects.all()
#     serializer_class = AutorSerializer



class ViewSetBase(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)


class PaginaViewSet(ViewSetBase):
    queryset = Pagina.objects.all()
    serializer_class = PaginaSerializer
    filter_fields = ('listas',)


class PlataformaViewSet(ViewSetBase):
    queryset = Plataforma.objects.all()
    serializer_class = PlataformaSerializer


# class CategoriaViewSet(ViewSetBase):
#     queryset = Categoria.objects.all()
#     serializer_class = CategoriaSerializer


class ListaViewSet(ViewSetBase):
    queryset = Lista.objects.all()
    serializer_class = ListaSerializer
    filter_fields = ('clasificador',)


# class DestacadoViewSet(ViewSetBase):
#     queryset = Destacado.objects.all()
#     serializer_class = DestacadoSerializer


class LinkViewSet(ViewSetBase):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


# class TipoViewSet(ViewSetBase):
#     queryset = Tipo.objects.all()
#     serializer_class = TipoSerializer


class ClasificadorViewSet(ViewSetBase):
    queryset = Clasificador.objects.all()
    serializer_class = ClasificadorSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class VideoViewSet(ViewSetBase):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_fields = ('id', 'slug', 'listas', 'estado', 'procesamiento', )

    def get_serializer_context(self):
        return {'request': self.request}


router = routers.DefaultRouter()
# router.register(r'autores', AutorViewSet)
# router.register(r'categorias', CategoriaViewSet)
router.register(r'clasificador', ClasificadorViewSet)
# router.register(r'destacados', DestacadoViewSet)
router.register(r'plataformas', PlataformaViewSet)
#router.register(r'listas', ListaViewSet)
router.register(r'links', LinkViewSet)
router.register(r'paginas', PaginaViewSet)
# router.register(r'series', SerieViewSet)
router.register(r'listas', ListaViewSet)
router.register(r'videos', VideoViewSet)
