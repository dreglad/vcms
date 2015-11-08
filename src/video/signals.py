# -*- coding: utf-8 -*-
from django.db.models.signals import post_init, pre_save, post_save, post_delete
from django.core.files.base import ContentFile
from django.conf import settings
from subprocess import Popen, PIPE, call
from django.dispatch import receiver
from clips.models import Clip
from video_ops import *
from video.jobs.ops import segmentar_video_job, sprites_job
import datetime
import time
import os



@receiver(post_save, sender=Clip)
def procesar_clip(sender, **kwargs):
    #try:
    clip = kwargs['instance']

    if clip.origen != Clip.ORIGEN_PROPIO:
        if not clip.transferido:
            clip.transferido = True
        return

    if clip.duracion or clip.fps == -1.0:
        return

    nombre_base = '%s-%s' % (datetime.datetime.now().strftime('%F'), clip.pk)
    nombre_imagen = 'imagen-%s.jpg' % nombre_base
    nombre_audio = 'audio-%s.mp3' % nombre_base
    nombre_clip = 'video-%s.mp4' % clip.pk

    try:
        cmd_duracion = 'ffmpeg -i %s 2>&1 | grep "Duration" | cut -d " " -f 4 | cut -d "." -f 1' % clip.archivo.path
        duracion = datetime.time(*time.strptime(Popen(cmd_duracion, stdout=PIPE, shell=True).stdout.read().strip(), '%H:%M:%S')[3:6])
        clip.duracion = duracion

        # TODO: Comando genérico para  obtener FPS
        # cmd_fps = 'ffmpeg -i %s 2>&1 | grep "tbr" | cut -d " " -f 11' % clip.archivo.path
        # fps = float(Popen(cmd_fps, stdout=PIPE, shell=True).stdout.read())
        clip.fps = 0

        cmd_bitrate = 'ffmpeg -i %s 2>&1 | grep "bitrate" | cut -d " " -f 8' % clip.archivo.path
        bitrate = float(Popen(cmd_bitrate, stdout=PIPE, shell=True).stdout.read())
        clip.bitrate = float(bitrate)

        offset = abs(int((clip.duracion.minute*60 + clip.duracion.second)/2))
        cmd_imagen = 'ffmpeg -y -ss %d -i %s -vframes 1 -an /tmp/%s' % (offset, clip.archivo.path, nombre_imagen)
        call(cmd_imagen, shell=True)
        imagen_content = ContentFile(open('/tmp/%s' % nombre_imagen, 'r').read())
        clip.imagen.save(nombre_imagen, imagen_content, save=False)
        os.remove('/tmp/%s' % nombre_imagen)

        cmd_audio = 'ffmpeg -y -i %s -vn -c:a libmp3lame -ar 44100 -b:a 128k -ac 1 /tmp/%s' % (clip.archivo.path, nombre_audio)
        call(cmd_audio, shell=True)
        audio_content = ContentFile(open('/tmp/%s' % nombre_audio, 'r').read())
        clip.audio.save(nombre_audio, audio_content, save=False)
        os.remove('/tmp/%s' % nombre_audio)

        clip.transferido = True
        clip.save()

        # Segments and sprites
        sprites_job.delay(clip.pk)
        segmentar_video_job.delay(clip.pk)

    except:
        clip.fps = -1.0
        clip.save()


# def obtener_geotag(sender, **kwargs):
#     import socket

#     socket.setdefaulttimeout(6.0)

#     clip = kwargs['instance']

#     if True:
#     #try:
#         if not clip.geotag and clip.pais and clip.procesado():
#             pais_query = clip.pais.nombre.strip() or clip.pais.codigo.strip()
#             ciudad_query = clip.ciudad and u'%s, ' % clip.ciudad.strip() or ''
#             estado_query = clip.estado and u'%s, ' % clip.estado.nombre or ''
#             g = geocoders.GoogleV3("ABQIAAAAA8RFVpQbXq3_qPZn9og-MxRUGD526XLMt3pQpgpur7Qd10fwihS1VNdNvYCHhqCx8Y0xdyGmMtke0g")
#             #g = geocoders.GeoNames()
#             try: place, (lat, lng) = g.geocode("%s%s%s" % (ciudad_query, estado_query, pais_query))
#             except:
#                 try: place, (lat, lng) = g.geocode(pais_query)
#                 except: lat, lng = (None, None)

#             if lat and lng:
#                 clip.geotag = u'%s,%s' % (lat, lng)
#                 clip.save()
#     #except:
#     #    pass
# post_save.connect(obtener_geotag, sender=Clip)


def reset_fps(sender, **kwargs):
    clip = kwargs['instance']
    if clip.fps == -1.0:
        clip.fps = -2.0


# def generar_archivo_subtitulado(sender, **kwargs):
#     clip = kwargs['instance']

#     if clip.procesado() and clip.subtitulos and not clip.archivo_subtitulado and clip.observaciones != 'subtitulando':

#         clip.observaciones = 'subtitulando'
#         clip.save()

#         try:
#             user = User.objects.get(username=clip.usuario_modificacion)
#         except:
#             user = User()

#         job = generar_archivo_subtitulado_job.delay(clip.pk, clip.archivo.path, clip.subtitulos.path, user.pk)

#         sleep(0.5)
#         if not job.is_started and user:
#             job.meta['retrasado'] = True
#             job.save()
#             message = u'%s, el SUBTITULAJE del clip %d que solicitaste aún no ha comenzado porque está esperando en cola.' % (user.first_name, clip.pk)
#             do_send_mail(u'SUBTITULAJE de clip %d retrasado' % clip.pk, message,
#                 'captura@correo.tlsur.net', [user.email],
#                 fail_silently=True)


# @job('recorte', timeout=7200)
# def recortar_clip_job(clip_pk, archivo_path, inicio, final, duracion, user_pk):
#     connection.close()
#     try:
#         user = User.objects.get(pk=user_pk)
#     except:
#         user = None

#     job = get_current_job()
#     temp_mp4 = '/mnt/captura-media/temp/recortado-%s.mp4' % clip_pk

#     if 'retrasado' in job.meta and user:
#         del job.meta['retrasado']
#         job.save()
#         message = u'%s, el RECORTE del clip %d que solicitaste y estaba en cola acaba de comenzar.' % (user.first_name, clip_pk)
#         do_send_mail(u'RECORTE de clip %d comenzado' % clip_pk, message,
#             'captura@correo.tlsur.net', [user.email],
#             fail_silently=True)

#     if not inicio and not final:
#         return

#     if not final:
#         final = duracion
#     if not inicio:
#         inicio = datetime.time(0)

#     if inicio > duracion or final > duracion or final < inicio:
#         clip = Clip.objects.get(pk=clip_pk)
#         clip.observaciones = (clip.observaciones or '') + "\nNo se pudo recorte_inicio debido a que los tiempos determinados son inválidos (inicio: %s, final: %s, duracion: %s). Tiempos especificados por el usuario: inicio: %s, final %s" % (inicio, final, clip.duracion, clip.recorte_inicio, clip.recorte_final)
#         clip.save(skip_fecha_modificacion=True)
#         return

#     def add_secs_to_time(timeval, secs_to_add):
#         secs = timeval.hour * 3600 + timeval.minute * 60 + timeval.second
#         secs += secs_to_add
#         return datetime.time(secs // 3600, (secs % 3600) // 60, secs % 60)
#     td = (datetime.datetime.strptime(str(final), '%H:%M:%S') - datetime.datetime.strptime(str(inicio), '%H:%M:%S'))
#     duracion = add_secs_to_time(datetime.time(0), td.seconds)

#     def recomprimir(path):
#         recomprimir_video = 'ffmpeg -y -i %s ' % path
#         recomprimir_video += '-ss %02d:%02d:%02d ' % (inicio.hour, inicio.minute, inicio.second)
#         recomprimir_video += '-t %02d:%02d:%02d ' % (duracion.hour, duracion.minute, duracion.second)
#         recomprimir_video += ' -c:a copy -async 1 -c:v libx264 -profile:v main -level:v 3.1 -threads 0 -movflags faststart %s' % temp_mp4
#         #recomprimir_video += ' -c:a copy -async 1 -c:v libx264 -flags +loop+mv4 -cmp 256 '
#         #recomprimir_video += '-partitions +parti4x4+parti8x8+partp4x4+partp8x8+partb8x8 -me_method hex -subq 7 '
#         #recomprimir_video += '-trellis 1 -refs 5 -bf 0 -coder 0 -me_range 16 -g 250 -keyint_min 25 '
#         #recomprimir_video += '-sc_threshold 40 -i_qfactor 0.71 -qmin 10 -qmax 51 -qdiff 4 -threads 0 -movflags faststart %s' % temp_mp4
#         call(recomprimir_video, shell=True)
#         #call('mp4file --optimize %s' % temp_mp4, shell=True)

#     recomprimir(archivo_path)
#     recortado_content = ContentFile(open(temp_mp4, 'r').read())

#     connection.close()

#     clip = Clip.objects.get(pk=clip_pk)
#     clip.archivo.save(os.path.basename(clip.archivo.name), recortado_content, save=False)
#     clip.transferido = False
#     clip.duracion = duracion
#     clip.observaciones = (clip.observaciones or '') + "\nRecortado el %s por %s" % (datetime.datetime.now().strftime('%Y-%m-%d'), user.username if user else 'alguien')
#     clip.save()

#     if clip.archivo_subtitulado:
#         recomprimir(clip.archivo_subtitulado.path)

#         clip = Clip.objects.get(pk=clip_pk)
#         recortado_content = ContentFile(open(temp_mp4, 'r').read())
#         clip.archivo_subtitulado.save(os.path.basename(clip.archivo_subtitulado.name), recortado_content, save=False)
#         clip.save()

#     clip.resolucion = 0  # segmenta de nuevo
#     clip.save()
#     os.remove(temp_mp4)

#     if user:
#         message = u'%s recortó clip:\nhttp://captura-telesur.openmultimedia.biz/admin/clips/clip/%s/\n\nArchivo recortado:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.username, clip_pk, clip.archivo.url)
#         do_send_mail('Clip RECORTADO %s por %s' % (clip_pk, user.username), message,
#             'captura@correo.tlsur.net', ['multimedia_edicion@correo.tlsur.net'],
#             fail_silently=False)

#         message = u'%s, el RECORTE del clip %d que solicitaste ha finalizado.\n\nEl clip es:\nhttp://captura-telesur.openmultimedia.biz/admin/clips/clip/%s/\n\nArchivo de video:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.first_name, clip_pk, clip_pk, clip.archivo.url)
#         do_send_mail(u'RECORTE de clip %d finalizado' % clip_pk, message,
#             'captura@correo.tlsur.net', [user.email],
#             fail_silently=True)


# def recortar_clip(sender, **kwargs):
#     clip = kwargs['instance']

#     if clip.procesado() and (clip.recorte_inicio or clip.recorte_final):
#         try:
#             user = User.objects.get(username=clip.usuario_modificacion)
#         except:
#             user = User()

#         job = recortar_clip_job.delay(clip.pk, clip.archivo.path, clip.recorte_inicio, clip.recorte_final, clip.duracion, user.pk)
#         clip.recorte_inicio = None
#         clip.recorte_final = None
#         clip.save(skip_fecha_modificacion=True)

#         sleep(0.5)
#         if not job.is_started:
#             job.meta['retrasado'] = True
#             job.save()
#             message = u'%s, el RECORTE del clip %d que solicitaste aún no ha comenzado porque está esperando en cola.' % (user.first_name, clip.pk)
#             do_send_mail(u'RECORTE de clip %d retrasado' % clip.pk, message,
#                 'captura@correo.tlsur.net', [user.email],
#                 fail_silently=True)



def segmentar_video(sender, **kwargs):
    clip = kwargs['instance']
    if not clip.resolucion:
        r = redis.Redis('localhost', db=2)
        key = 'segmentar-%d' % clip.pk
        if not r.get(key):
            r.incr(key)
            segmentar_video_job.delay(clip.pk)





def sprites(sender, **kwargs):
    clip = kwargs['instance']
    if not clip.sprites:
        r = redis.Redis('localhost', db=2)
        key = 'sprites-%d' % clip.pk
        if not r.get(key):
            r.incr(key)
            Clip.objects.filter(pk=clip.id).update(sprites=-1)
            sprites_job.delay(clip.pk)


# def delete_files(sender, **kwargs):
#     clip = kwargs['instance']
#     file_attrs = ('archivo', 'imagen', 'audio', 'subtitulos')
#     for file_attr in file_attrs:
#         attr = getattr(clip, file_attr)
#         if attr:
#             # archivo, audio and imagen may be shared in translated clips, dont delete them
#             if (clip.clip_original_id or clip.traducciones.count()) and file_attr in ['archivo', 'audio', 'imagen']:
#                 return
#             else:
#                 attr.delete(save=False)
# post_delete.connect(delete_files, sender=Clip)


# Connect model signal receivers

# post_save.connect(procesar_clip, sender=Clip)
post_init.connect(reset_fps, sender=Clip)
#post_save.connect(segmentar_video, sender=Clip)
#post_save.connect(sprites, sender=Clip)
# post_save.connect(recortar_clip, sender=Clip)
# post_save.connect(crear_traducciones, sender=Clip)
# post_save.connect(generar_archivo_subtitulado, sender=Clip)


