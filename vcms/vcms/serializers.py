# -*- coding: utf-8 -*- #
from rest_framework import serializers
from rest_framework.fields import URLField

from videos.models import *
from sorl.thumbnail import get_thumbnail


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


class VideoSerializer(serializers.HyperlinkedModelSerializer):
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


class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'slug', 'nombre')

class ListaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lista
        fields = ('id', 'slug', 'tipo', 'nombre', 'descripcion',
            'descripcion_plain', 'usar_nombre', 'usar_descripcion', 'layout',
            'categoria', 'usar_web', 'usar_movil', 'usar_tv', 'ads_web',
            'ads_movil', 'ads_tv', 'fecha_creacion', 'fecha_modificacion',
            'tags', 'videos',
            )

class TipoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tipo
        fields = ('id', 'slug', 'nombre', 'nombre_plural', 'descripcion')

class AutorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Autor
        fields = ('id', 'slug', 'nombre')

class SitioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sitio
        fields = ('id', 'slug', 'nombre')