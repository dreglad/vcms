from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='seccion')
def seccion(video, clasificador='seccion', valor=None):
    return video.clasificacion(clasificador, valor)

