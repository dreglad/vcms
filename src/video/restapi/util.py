# -*- coding: utf-8 -*-
from django.db.models import Model
from django.db.models import Q
import re
import md5

NUM_MAX_NUM_RESULTS = 300
NUM_DEFAULT_RESULTS = 30

def validar_request(request_params):
    if 'autenticado' in request_params:
        return True
    if not 'signature' in request_params or not request_params['signature']:
        return False

    if 'key' in request_params and request_params['key'] == 'soyreportero':
        secret = 'Tl&MF4s#e-9x6F[m7]42FyO7mt8Ku'
    else:
        return False

    cadena = u'%s' % secret
    for key in sorted(request_params.iterkeys()):
        if key == 'signature': continue
        cadena += '%s%s' % (key, request_params[key])

    firma = md5.new(cadena).hexdigest()

    return firma == request_params['signature']

def clip_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ForeignKey
    opts = instance._meta
    data = {}
    forfields = fields if fields else [f.name for f in opts.fields + opts.many_to_many]

    for f in forfields:
        if exclude and f in exclude:
            continue
        val = getattr(instance, f)
        if callable(val):
            val = val()
        if isinstance(val, Model):
            # If the object doesn't have a primry key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f] = []
            else:
                obj_rel = val
                if obj_rel:
                    for f_rel in obj_rel.__class__._meta.fields:
                        relname = f+'__'+f_rel.name
                        if exclude and relname in exclude:
                            continue
                        data[relname] = f_rel.value_from_object(obj_rel)
        else:
            data[f] = val

    return data

def paginar(request, queryset):
    if request.GET.get('return') == 'count':
        return queryset.count()

    primero = int(request.GET.get('primero', int(request.GET.get('offset', 0))+1))
    ultimo =  int(request.GET.get('ultimo', int(request.GET.get('limit', NUM_DEFAULT_RESULTS)) + primero-1))

    if ultimo - primero > NUM_MAX_NUM_RESULTS:
        if primero > 1:
            ultimo = primero + NUM_MAX_NUM_RESULTS
        else:
            primero = ultimo - NUM_MAX_NUM_RESULTS

    return queryset[primero-1:ultimo]

def filtrar_con_busqueda_texto(queryset, texto, campos):
    u"""
    Devuelve el 'queryset' acotado con una busqueda de 'texto' sobre los 'campos' especificados
    """
    if not texto: return queryset
    texto = texto.strip()
    if len(texto) < 2: return queryset
    q1 = Q()
    q2 = Q()
    palabras = [p for p in [texto] + texto.split(' ') if len(p) > 1]
    for palabra in palabras:
        if palabra.startswith('-'):
            palabra = palabra[1:]
            for campo in campos:
                q2 = q2 & Q(**{'%s__icontains' % campo: palabra})
        else:
            for campo in campos:
                q1 = q1 | Q(**{'%s__icontains' % campo: palabra})
    return queryset.filter(q1, q2)


def filtrar_con_clip_relacionado(queryset):
    # return queryset.filter(clip__isnull=False, clip__publicado=True, clip__transferido=True, clip__idioma_original=views.CURRENT_LANGUAGE).distinct()
    #return queryset.filter(clip__isnull=False, clip__publicado=True, clip__transferido=True).distinct()
    return queryset

def filtrar_con_programa_relacionado(queryset):
    """
    Devuelve el 'queryset' acotado con objetos que al menos tienen una relación con algún Clip
    Esto sirve por ejemplo para no devolver "secciones vacías"
    """
    #return queryset.filter(programa__clip__isnull=False, programa__clip__publicado=True, programa__clip__transferido=True).distinct()
    return queryset


RE_EXCEPTO = re.compile(r'^excepto__(.+)$')
def filtrar_con_campo(queryset, values, lookup):
        if not values or (len(values) == 1 and not values[0]): return queryset
        q = Q()
        for cat in values:
            if cat in ('null', 'es_nulo', 'notnull', 'no_es_nulo'):
                es_nulo = cat in ('null', 'es_nulo')
                queryset = queryset.filter(**{'%s__isnull' % lookup: es_nulo})
            else:
                m = re.match(RE_EXCEPTO, str(cat))
                if m:
                    q = q | ~Q(**{lookup: m.group(1)})
                else:
                    q = q | Q(**{lookup: cat})
        if values: queryset = queryset.filter(q)

        return queryset

