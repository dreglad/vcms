# -*- coding: utf-8 -*- #
import json
import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from rest_framework import mixins, routers, serializers, viewsets
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
class AutorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Autor
        fields = ('id', 'slug', 'nombre')


class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'slug', 'nombre')


class ListaSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagsField(read_only=True)
    class Meta:
        model = Lista
        fields = ('id', 'slug', 'tipo', 'nombre', 'descripcion',
            'descripcion_plain', 'usar_nombre', 'usar_descripcion', 'layout',
            'categoria', 'usar_web', 'usar_movil', 'usar_tv', 'ads_web',
            'ads_movil', 'ads_tv', 'fecha_creacion', 'fecha_modificacion',
            'tags', 'videos',
            )


class SitioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sitio
        fields = ('id', 'slug', 'nombre')


class TipoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tipo
        fields = ('id', 'slug', 'nombre', 'nombre_plural', 'descripcion')


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagsField(read_only=True)
    thumbnail_100 = HyperlinkedSorlImageField('100',
        source='imagen', read_only=True
        )
    thumbnail_250 = HyperlinkedSorlImageField('250',
        source='imagen', read_only=True
        )
    thumbnail_500 = HyperlinkedSorlImageField('500',
        source='imagen', read_only=True
        )
    thumbnail_1000 = HyperlinkedSorlImageField('1000',
        source='imagen', read_only=True
        )
    tags 

    url = URLField(source='get_absolute_url')
    class Meta:
        model = Video
        fields = ('id', 'estado', 'procesamiento', 'slug', 'fecha', 'url',
            'origen', 'origen_url', 'youtube_id', 'duracion', 'original_width',
            'original_height', 'resolucion', 'hls', 'archivo', 'sprites',
            'captions', 'imagen', 'thumbnail_100', 'thumbnail_250',
            'thumbnail_500', 'thumbnail_1000', 'titulo', 'resumen',
            'descripcion', 'descripcion_plain', 'transcripcion',  'tipo',
            'categoria', 'autor', 'fecha_creacion', 'fecha_modificacion',
            'listas', 'tags')


"""
Viewsets
"""
class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ListaViewSet(viewsets.ModelViewSet):
    queryset = Lista.objects.all()
    serializer_class = ListaSerializer


class SitioViewSet(viewsets.ModelViewSet):
    queryset = Sitio.objects.all()
    serializer_class = SitioSerializer


class TipoViewSet(viewsets.ModelViewSet):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_context(self):
        return {'request': self.request}


router = routers.DefaultRouter()
router.register(r'autores', AutorViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'listas', ListaViewSet)
router.register(r'sitios', SitioViewSet)
router.register(r'tipos', TipoViewSet)
router.register(r'videos', VideoViewSet)