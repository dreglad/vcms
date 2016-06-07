# # -*- coding: utf-8 -*- #
# from rest_framework import routers, serializers, viewsets
# from video.models import *


# # Serializers define the API representation.
# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = ('id', 'slug', 'origen', 'fecha', 'tipo', 'titulo', 'descripcion',
#                   'player_url', 'archivo_url', 'hls_url', 'sprites_url',
#                   'aspect', 'duracion', 'resolucion',
#                   'descarga_url', 'audio_url', 'thumbnail_pequeno',
#                   'thumbnail_mediano', 'thumbnail_grande', 'vistas',
#                   'categoria', 'programa', 'tema', 'corresponsal', 'pais',
#                   'serie', 'capitulo',)

# class CategoriaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Categoria
#         fields = ('id', 'slug', 'nombre')

# class SerieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Serie
#         fields = ('id', 'slug', 'nombre', 'descripcion')

# class ProgramaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Programa
#         fields = ('id', 'nombre', 'descripcion', 'horario', 'tipo',)

# class TipoProgramaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TipoPrograma
#         fields = ('id', 'nombre')

# class TipoVideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TipoVideo
#         fields = ('id', 'nombre', 'nombre_plural', 'descargable')

# class PaisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pais
#         fields = ('id', 'nombre', 'codigo', 'ubicacion')

# class TemaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tema
#         fields = ('id', 'nombre', 'descripcion', 'fecha_creacion')

# class CorresponsalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Corresponsal
#         fields = ('id', 'nombre', 'twitter', 'email', 'pais')



# # ViewSets define the view behavior.
# class VideoViewSet(viewsets.ModelViewSet):
#     queryset = Video.objects.filter(publicado=True, procesado=True)
#     serializer_class = VideoSerializer
#     filter_fields = ('tipo', 'programa', 'categoria', 'pais',
#                      'corresponsal', 'serie', 'origen')
#     search_fields = ('titulo', 'descripcion')

# class CategoriaViewSet(viewsets.ModelViewSet):
#     queryset = Categoria.objects.all()
#     serializer_class = CategoriaSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)

# class ProgramaViewSet(viewsets.ModelViewSet):
#     queryset = Programa.objects.all()
#     serializer_class = ProgramaSerializer
#     filter_fields = ('tipo',)
#     search_fields = ('nombre',)

# class SerieViewSet(viewsets.ModelViewSet):
#     queryset = Serie.objects.all()
#     serializer_class = SerieSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)

# class TipoProgramaViewSet(viewsets.ModelViewSet):
#     queryset = TipoPrograma.objects.all()
#     serializer_class = TipoProgramaSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)

# class TipoVideoViewSet(viewsets.ModelViewSet):
#     queryset = TipoVideo.objects.all()
#     serializer_class = TipoVideoSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)

# class PaisViewSet(viewsets.ModelViewSet):
#     queryset = Pais.objects.all()
#     serializer_class = PaisSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)

# class TemaViewSet(viewsets.ModelViewSet):
#     queryset = Tema.objects.all()
#     serializer_class = TemaSerializer
#     filter_fields = ('nombre',)
#     search_fields = ('nombre',)



# # Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'video', VideoViewSet)
# router.register(r'tipo_video', TipoVideoViewSet)
# router.register(r'categoria', CategoriaViewSet)
# router.register(r'programa', ProgramaViewSet)
# router.register(r'tipo_programa', TipoProgramaViewSet)
# router.register(r'serie', SerieViewSet)
# router.register(r'tema', TemaViewSet)
# router.register(r'pais', PaisViewSet)

