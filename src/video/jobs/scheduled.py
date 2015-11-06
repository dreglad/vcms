# -*- coding: utf-8 -*- #
#coding=utf-8
from django.conf import settings
import datetime
import time
from django import db
from django.db.models import Q
from clips.models import Distribucion, Distribuido
from math import log
import mandrill
from ftplib import FTP

def send_mail(template_name, email_to, subject, context):
    API_KEY = '_K1uR6XstPi4bWjbL3YxnA'
    mandrill_client = mandrill.Mandrill(API_KEY)
    message = {
        'to': [],
        'global_merge_vars': [],
        'subject': subject
    }
    for em in email_to:
        message['to'].append({'email': em})

    for k, v in context.iteritems():
        message['global_merge_vars'].append(
            {'name': k, 'content': v}
        )
    mandrill_client.messages.send_template(template_name, [], message)

def sizeof_fmt(num):
    """Human friendly file size"""
    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def get_clip_context(clip):
    context = {
        'clip_fecha': clip.fecha.strftime('%Y-%m-%d'), 'clip_tipo': clip.tipo.nombre,
        'clip_titulo': clip.titulo, 'clip_descripcion': clip.descripcion,
        'clip_thumbnail_url': clip.thumbnail_grande(),
        'clip_descarga_url': clip.get_archivo_storage_url() + '?descargar',
        'clip_duracion': str(clip.duracion),
        'clip_filesize': sizeof_fmt(clip.archivo.size),
        'clip_url': clip.make_url(),
        'clip_slug': clip.slug
    }
    if clip.programa: context.update(clip_programa=clip.progsrama.nombre)
    if clip.categoria: context.update(clip_categoria=clip.categoria.nombre)
    if clip.corresponsal: context.update(clip_corresponsal=clip.corresponsal.nombre)
    if clip.hashtags: context.update(clip_hashtags=clip.hashtags)
    if clip.tema: context.update(clip_tema=clip.tema.nombre)
    if clip.serie: context.update(clip_serie=clip.serie.nombre)
    if clip.pais: context.update(clip_pais=clip.pais.nombre)

    # static context
    if clip.idioma_original == 'en':
        context.update({
            'static_heading': 'VIDEO PUBLISHED NOTIFICATION',
            'static_saludo': 'This is a notification that a new video was recently published on our platform:',
            'static_descargar': 'Download video',
            'static_ficha': 'Fact sheet',
            'static_fecha': 'Date',
            'static_tipo': 'Type',
            'static_duracion': u'Duration',
            'static_categoria': 'Category',
            'static_programa': 'Show',
            'static_serie': 'Series',
            'static_corresponsal': 'Correspondent',
            'static_tema': 'Topic',
            'static_pais': 'Country',
            'static_entrevistado': 'Interviewed',
            'static_entrevistador': 'Interviewer',
            'static_verweb': 'View in website',
            'static_enviado_a': 'This notification message was sent to ',
            'static_enviado_porque': "because our automated notification systems's records indicate your desire to receive them.",
            'static_unsuscribe': 'If you no longer want to get this kinkd of notifications, please reach us at:',
            'static_videoteca': 'Video library',
            'static_sitioweb': 'Web site',
        })
    else:
        context.update({
            'static_heading': u'NOTIFICACIÓN DE VIDEO PUBLICADO',
            'static_saludo': u'Mediante este mensaje se le notifica la reciente publicación en nuestra plataforma del clip de video titulado:',
            'static_descargar': u'Descargar video',
            'static_ficha': u'Ficha técnica',
            'static_fecha': u'Fecha',
            'static_tipo': u'Tipo',
            'static_duracion': u'Duración',
            'static_categoria': u'Categoría',
            'static_programa': u'Programa',
            'static_serie': u'Series',
            'static_corresponsal': u'Corresponsal',
            'static_tema': u'Topic',
            'static_pais': u'Country',
            'static_entrevistado': u'Entrevistado',
            'static_entrevistador': u'Entrevistador',
            'static_verweb': u'Ver en sitio web',
            'static_enviado_a': u'Este mensaje de correo electrónico fue enviado a',
            'static_enviado_porque': u'debido a que nuestras reglas de distribución automática de clips de video indican que usted así lo desea.',
            'static_unsuscribe': u'Si usted no desea seguir recibiendo este tipo de mensajes por favor contáctenos en:',
            'static_videoteca': u'Videoteca',
            'static_sitioweb': u'Sitio web',
        })

    return context


def distribucion_job():
    #db.close_connection()
    print(u"-------------------------------------------")
    print(u"Fecha: %s" % datetime.datetime.now())
    print(u"-------------------------------------------")

    for distribucion in Distribucion.objects.filter(activo=True):
        print(u"Iniciando con distribucion: %s" % distribucion)

        distribuidos_pks = distribucion.distribuidos.values_list('clip__pk', flat=True)
        clips = distribucion.get_clips_distribuibles().exclude(pk__in=distribuidos_pks).order_by('fecha')
        print(u"Total clips seleccionados para distribuir: %s" % clips.count())

        if distribucion.email:
            for clip in clips[:30]:
                print(u"Distribuyendo por email clip: %s" % clip)
                dist = Distribuido(status=1, clip=clip, distribucion=distribucion)
                sent = False

                context = get_clip_context(clip)

                if clip.idioma_original == 'en':
                    subject = u'Video published notification: %s' % clip.titulo
                else:
                    subject = u'Notificación de clip publicado: %s' % clip.titulo
                for email in distribucion.get_email_dict():
                    if email[1] == 'CORRESPONSAL':
                        if clip.corresponsal and clip.corresponsal.email:
                            print(u'Distribuyendo a corresponsal')
                            email = (clip.corresponsal.nombre, clip.corresponsal.email)
                        else:
                            print(u'Sin correpsonsal o sin email: %s' % clip.corresponsal)
                            continue

                    print(u'Distribuyendo a %s <%s>' % (email[0], email[1]))
                    context.update({'to_name': email[0], 'to_email': email[1]})
                    result = send_mail(distribucion.email_template, [email[1]], subject, context=context)
                    sent = True

                if sent:
                    dist.status = 3  # completado
                    dist.save()
                    time.sleep(1)

        elif distribucion.ftp_host:
            for clip in clips[:30]:
                print(u"Distribuyendo por FTP clip: %s" % clip)
                dist = Distribuido(status=1, clip=clip, distribucion=distribucion)

                # Subir por FTP
                ftp = FTP(distribucion.ftp_host, distribucion.ftp_user, distribucion.ftp_pass, timeout=7200)

                try:
                    filename = '%s_%s_%s.mp4' % (clip.pk, clip.programa.slug if clip.programa else clip.slug, clip.fecha.strftime('%Y-%m-%d'))
                    ftp.cwd(distribucion.ftp_dir)
                    ftp.storbinary('STOR %s' % filename, open(clip.archivo.path, 'rb'))
                except Exception, e:
                    print(u"ERROR subiendo por FTP: %s" % e)
                dist.status = 3  # completado
                dist.save()
                time.sleep(1)

        print(u"Terminando con clip")

