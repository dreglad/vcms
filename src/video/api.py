# -*- coding: utf-8 -*- #
from rest_framework import routers, serializers, viewsets
from clips.models import *


# Serializers define the API representation.
class ClipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clip
        fields = ('id', 'titulo', 'descripcion', 'fecha')

class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'nombre')

class SerieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Serie
        fields = ('id', 'nombre', 'descripcion')

class ProgramaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Programa
        fields = ('id', 'nombre', 'descripcion', 'horario', 'tipo')

class TipoProgramaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TipoPrograma
        fields = ('id', 'nombre')

class TipoClipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TipoClip
        fields = ('id', 'nombre', 'nombre_plural', 'descargable')

class PaisSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pais
        fields = ('nombre', 'codigo', 'ubicacion', 'geotag')

class TemaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tema
        fields = ('nombre', 'descripcion', 'fecha_creacion')

class CorresponsalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corresponsal
        fields = ('nombre', 'twitter', 'email', 'pais')



# ViewSets define the view behavior.
class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer

class SerieViewSet(viewsets.ModelViewSet):
    queryset = Serie.objects.all()
    serializer_class = SerieSerializer

class TipoProgramaViewSet(viewsets.ModelViewSet):
    queryset = TipoPrograma.objects.all()
    serializer_class = TipoProgramaSerializer

class TipoClipViewSet(viewsets.ModelViewSet):
    queryset = TipoClip.objects.all()
    serializer_class = TipoClipSerializer

class PaisViewSet(viewsets.ModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer

class CorresponsalViewSet(viewsets.ModelViewSet):
    queryset = Corresponsal.objects.all()
    serializer_class = CorresponsalSerializer

class TemaViewSet(viewsets.ModelViewSet):
    queryset = Tema.objects.all()
    serializer_class = TemaSerializer



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'clip', ClipViewSet)
router.register(r'tipo_clip', TipoClipViewSet)
router.register(r'categoria', CategoriaViewSet)
router.register(r'programa', ProgramaViewSet)
router.register(r'tipo_programa', TipoProgramaViewSet)
router.register(r'serie', SerieViewSet)
router.register(r'tema', TemaViewSet)
router.register(r'corresponsal', CorresponsalViewSet)
router.register(r'pais', PaisViewSet)

