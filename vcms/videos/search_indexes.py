# -*- coding: utf-8 -*- #
import datetime

from elasticstack.fields import CharField
from haystack import indexes

from .models import Video, Lista


class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = CharField(document=True, use_template=True,
            analyzer='synonym_analyzer')
    fecha = indexes.DateTimeField(model_attr='fecha')
    listas = indexes.MultiValueField()
    clasificadores = indexes.MultiValueField()
    autor = indexes.CharField()
    serie = indexes.CharField()
    formato = indexes.CharField()
    tags = indexes.MultiValueField()

    def get_model(self):
        return Video

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.publicos().prefetch_related('listas')

    def prepare_listas(self, obj):
        return [lista.nombre for lista in obj.listas.all()]

    def prepare_autor(self, obj):
        lista = obj.get_clasificacion('autor')
        if lista: return lista.nombre

    def prepare_serie(self, obj):
        lista = obj.get_clasificacion('serie')
        if lista: return lista.nombre

    def prepare_formato(self, obj):
        lista = obj.get_clasificacion('formato')
        if lista and isinstance(lista, Lista):
            return lista.nombre

    def prepare_tags(self, obj):
        total_tags = set([tag.name for tag in obj.tags.all()])
        for lista in obj.listas.all():
            total_tags = total_tags | set([tag.name for tag in lista.tags.all()])
        return total_tags

    def prepare_clasificadores(self, obj):
        clasificadores = set()
        for lista in obj.listas.all():
            clasificadores.add(lista.clasificador.nombre)
        return list(clasificadores)