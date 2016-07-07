# -*- coding: utf-8 -*- #
import datetime

from elasticstack.fields import CharField
from haystack import indexes

from .models import Video


class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = CharField(document=True, use_template=True,
            analyzer='synonym_analyzer')
    fecha = indexes.DateTimeField(model_attr='fecha')
    listas = indexes.MultiValueField()
    tags = indexes.MultiValueField()

    def get_model(self):
        return Video

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.publicos().prefetch_related('listas')

    def prepare_listas(self, obj):
        return [lista.nombre for lista in obj.listas.all()]

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]