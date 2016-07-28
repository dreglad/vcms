import os
from math import ceil, floor
import random

from django import template
from django.utils.safestring import mark_safe

from videos.models import Lista, Pagina, Video

register = template.Library()


@register.filter()
def display_attr(obj, attr):
    if hasattr(obj, 'get_display_attr'):
        return obj.get_display_attr(attr)

@register.assignment_tag()
def get_display_attrs(obj):
    attrs = (
        'tema', 'layout', 'margen', 'mostrar_nombre', 'mostrar_descripcion',
        'mostrar_maximo', 'mostrar_paginacion', 'texto_paginacion',
        'mostrar_publicidad', 'slug',
    )
    return {k:v for k, v in [(attr, display_attr(obj, attr)) for attr in attrs]}


@register.assignment_tag(takes_context=True)
def get_thumb_geometry(context, video, default='640x360'):
    large = '1280x720'
    if context.get('importante'):
        return large
    return default


@register.assignment_tag()
def get_clasificacion(video, clasificador=None):
    try:
        return video.get_clasificacion(clasificador)
    except:
        return None


@register.filter()
def clasificacion(video, clasificador=None):
    try:
        return video.get_clasificacion(clasificador)
    except:
        return None


@register.filter(name='getattr')
def object_attr(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)


@register.filter(name='lista_generica')
def lista_generica(lista, nombre=None):
    return {
        'videos': {'publicos': [x.object for x in lista]},
        'nombre': nombre,
    }

@register.filter()
def result_list(results):
    return [x.object for x in results]


@register.filter(name='pagina')
def pagina(video, clasificador):
    try:
        return video.listas.get(clasificador__slug=clasificador).slug
    except video.paginas.model.DoesNotExist:
        return None

@register.filter(name='breaksentence')
def breaksentence(text, min_words=4, thresshold=0.3):
    """
    Breaks a sentence into spans to balance uneven lines

    Usgae:

    {{ "Quisque tempor diam a sem, pellentesque|breaksentence }}

    Resulting DOM:
    <span class="broken">
      <span class="by-2">Quisque tempor diam a sem,</span>
      <span class="by-2">pellentesque aliquet</span>
    </span>

    Ugly:
    *--------------------------------------------*
    |   Quisque tempor diam a sem, pellentesque  |
    |   aliquet                                  |
    *--------------------------------------------*

    Pretty:
    *--------------------------------------------*
    |   Quisque tempor diam a sem,               |
    |   pellentesque aliquet                     |
    *--------------------------------------------*
    """

    def balance(words, addition=0):
        cutpoint = (len(words)/2) + addition
        halfs = (words[:cutpoint], words[cutpoint:])
        lengths = map(lambda x: len(''.join(x)), halfs)
        recommended_addition = 1 if lengths[0] < lengths[1] else -1
        return (
            [' '.join(words) for words in halfs],
            abs(lengths[0]-lengths[1])/float(lengths[0]),
            recommended_addition
        )
    words = text.split()
    if len(words) < min_words:
        parts = [text]
    else:
        parts, ratio, recomended = balance(words, 0)
        if ratio > thresshold:
            parts, second_ratio, second_recomended = balance(words, recomended)
            if second_ratio > ratio:
                parts, r, c = balance(words, second_recomended)

    return mark_safe('<span class="broken">%s</span>' % \
                ' '.join(['<span class="by-%d">%s</span>' % (len(parts), part)
                     for part in parts]).replace(' ...', '...'))


@register.filter(name='duration')
def duration(timedelta):
    if not timedelta: return timedelta
    hours, remainder = divmod(timedelta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    if minutes > 50: minutes = 0; hours += 1
    if seconds > 50: seconds = 0; minutes += 1
    if minutes and minutes < 10 and hours: minutes = 0; hours -= 1
    if seconds and seconds < 10 and minutes: seconds = 0; minutes -= 1
    if seconds in range(26, 34): seconds = 30
    if minutes in range(26, 34): minutes = 30

    duration = []
    if hours: duration.append(u'%d hr' % hours)
    if minutes: duration.append(u'%d min' % minutes)
    if seconds and not (hours and minutes): duration.append(u'%d seg' % seconds)
    return ', '.join(duration)


@register.tag(name="randomgen")
def randomgen(parser, token):
    items = []
    bits =  token.split_contents()
    for item in bits:
        items.append(item)
    return RandomgenNode(items[1:])

class RandomgenNode(template.Node):
    def __init__(self, items):
        self.items = []
        for item in items:
            self.items.append(item)
    
    def render(self, context):
        arg1 = self.items[0]
        arg2 = self.items[1]
        if "hash" in self.items:
            result = os.urandom(16).encode('hex')
        elif "float" in self.items:
            result = random.uniform(int(arg1), int(arg2))
        elif not self.items:
            result = random.random()
        else:
            result = random.randint(int(arg1), int(arg2))
        return result