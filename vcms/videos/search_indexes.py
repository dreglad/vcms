# -*- coding: utf-8 -*- #
import datetime

from haystack import indexes

from .models import Video


class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #autor = indexes.CharField(model_attr='autor')
    fecha = indexes.DateTimeField(model_attr='fecha')
    categoria = indexes.CharField(model_attr='categoria', null=True)
    tipo = indexes.CharField(model_attr='tipo', null=True)
    autor = indexes.CharField(model_attr='autor', null=True)
    tags = indexes.MultiValueField()

    def get_model(self):
        return Video

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.publicos().select_related('categoria', 'autor', 'tipo')

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_autor(self, obj):
        if obj.autor: return obj.autor.nombre

    def prepare_categoria(self, obj):
        if obj.categoria: return obj.categoria.nombre

    def prepare_tipo(self, obj):
        if obj.tipo: return obj.tipo.nombre