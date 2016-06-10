# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils.cache import get_cache_key

from .jobs.ops import crear_nuevo_video_job
from .video_ops import *
from videos.models import Video

@receiver(post_save, sender=Video)
def procesar_video(sender, **kwargs):
    video = kwargs['instance']

    if video.procesamiento == Video.PROCESAMIENTO.nuevo:
        status_path = os.path.join(settings.TEMP_ROOT, 'status', video.uuid)
        with open(status_path, 'w') as status_file:
            status_file.write('queue')

        video.procesamiento = Video.PROCESAMIENTO.procesando
        video.save()
        crear_nuevo_video_job.delay(video.pk)




# @receiver(post_save, sender=Video)
# def procesar_video(sender, **kwargs):
#     #try:
#     video = kwargs['instance']

#     if video.origen != Video.ORIGEN_PROPIO:
#         if not video.procesado:
#             video.procesado = True
#         return

#     if video.duracion or video.fps == -1.0:
#         return

#     nombre_base = '%s-%s' % (datetime.datetime.now().strftime('%F'), video.pk)
#     nombre_imagen = 'imagen-%s.jpg' % nombre_base
#     nombre_audio = 'audio-%s.mp3' % nombre_base
#     nombre_video = 'video-%s.mp4' % video.pk

#     try:
#         cmd_duracion = 'ffmpeg -i %s 2>&1 | grep "Duration" | cut -d " " -f 4 | cut -d "." -f 1' % video.archivo.path
#         duracion = datetime.time(*time.strptime(Popen(cmd_duracion, stdout=PIPE, shell=True).stdout.read().strip(), '%H:%M:%S')[3:6])
#         video.duracion = duracion

#         # TODO: Comando genérico para  obtener FPS
#         # cmd_fps = 'ffmpeg -i %s 2>&1 | grep "tbr" | cut -d " " -f 11' % video.archivo.path
#         # fps = float(Popen(cmd_fps, stdout=PIPE, shell=True).stdout.read())
#         video.fps = 0

#         cmd_bitrate = 'ffmpeg -i %s 2>&1 | grep "bitrate" | cut -d " " -f 8' % video.archivo.path
#         bitrate = float(Popen(cmd_bitrate, stdout=PIPE, shell=True).stdout.read())
#         video.bitrate = float(bitrate)

#         offset = abs(int((video.duracion.minute*60 + video.duracion.second)/2))
#         cmd_imagen = 'ffmpeg -y -ss %d -i %s -vframes 1 -an /tmp/%s' % (offset, video.archivo.path, nombre_imagen)
#         call(cmd_imagen, shell=True)
#         imagen_content = ContentFile(open('/tmp/%s' % nombre_imagen, 'r').read())
#         video.imagen.save(nombre_imagen, imagen_content, save=False)
#         os.remove('/tmp/%s' % nombre_imagen)

#         cmd_audio = 'ffmpeg -y -i %s -vn -c:a libmp3lame -ar 44100 -b:a 128k -ac 1 /tmp/%s' % (video.archivo.path, nombre_audio)
#         call(cmd_audio, shell=True)
#         audio_content = ContentFile(open('/tmp/%s' % nombre_audio, 'r').read())
#         video.audio.save(nombre_audio, audio_content, save=False)
#         os.remove('/tmp/%s' % nombre_audio)

#         video.procesado = True
#         video.save()

#         # Segments and sprites
#         sprites_job.delay(video.pk)
#         segmentar_video_job.delay(video.pk)

#     except:
#         video.fps = -1.0
#         video.save()


# def obtener_geotag(sender, **kwargs):
#     import socket

#     socket.setdefaulttimeout(6.0)

#     video = kwargs['instance']

#     if True:
#     #try:
#         if not video.geotag and video.pais and video.procesado():
#             pais_query = video.pais.nombre.strip() or video.pais.codigo.strip()
#             ciudad_query = video.ciudad and u'%s, ' % video.ciudad.strip() or ''
#             estado_query = video.estado and u'%s, ' % video.estado.nombre or ''
#             g = geocoders.GoogleV3("ABQIAAAAA8RFVpQbXq3_qPZn9og-MxRUGD526XLMt3pQpgpur7Qd10fwihS1VNdNvYCHhqCx8Y0xdyGmMtke0g")
#             #g = geocoders.GeoNames()
#             try: place, (lat, lng) = g.geocode("%s%s%s" % (ciudad_query, estado_query, pais_query))
#             except:
#                 try: place, (lat, lng) = g.geocode(pais_query)
#                 except: lat, lng = (None, None)

#             if lat and lng:
#                 video.geotag = u'%s,%s' % (lat, lng)
#                 video.save()
#     #except:
#     #    pass
# post_save.connect(obtener_geotag, sender=Video)


# def reset_fps(sender, **kwargs):
#     video = kwargs['instance']
#     if video.fps == -1.0:
#         video.fps = -2.0


# def generar_archivo_subtitulado(sender, **kwargs):
#     video = kwargs['instance']

#     if video.procesado() and video.subtitulos and not video.archivo_subtitulado and video.observaciones != 'subtitulando':

#         video.observaciones = 'subtitulando'
#         video.save()

#         try:
#             user = User.objects.get(username=video.usuario_modificacion)
#         except:
#             user = User()

#         job = generar_archivo_subtitulado_job.delay(video.pk, video.archivo.path, video.subtitulos.path, user.pk)

#         sleep(0.5)
#         if not job.is_started and user:
#             job.meta['retrasado'] = True
#             job.save()
#             message = u'%s, el SUBTITULAJE del video %d que solicitaste aún no ha comenzado porque está esperando en cola.' % (user.first_name, video.pk)
#             do_send_mail(u'SUBTITULAJE de video %d retrasado' % video.pk, message,
#                 'captura@correo.tlsur.net', [user.email],
#                 fail_silently=True)


# @job('recorte', timeout=7200)
# def recortar_video_job(video_pk, archivo_path, inicio, final, duracion, user_pk):
#     connection.close()
#     try:
#         user = User.objects.get(pk=user_pk)
#     except:
#         user = None

#     job = get_current_job()
#     temp_mp4 = '/mnt/captura-media/temp/recortado-%s.mp4' % video_pk

#     if 'retrasado' in job.meta and user:
#         del job.meta['retrasado']
#         job.save()
#         message = u'%s, el RECORTE del video %d que solicitaste y estaba en cola acaba de comenzar.' % (user.first_name, video_pk)
#         do_send_mail(u'RECORTE de video %d comenzado' % video_pk, message,
#             'captura@correo.tlsur.net', [user.email],
#             fail_silently=True)

#     if not inicio and not final:
#         return

#     if not final:
#         final = duracion
#     if not inicio:
#         inicio = datetime.time(0)

#     if inicio > duracion or final > duracion or final < inicio:
#         video = Video.objects.get(pk=video_pk)
#         video.observaciones = (video.observaciones or '') + "\nNo se pudo recorte_inicio debido a que los tiempos determinados son inválidos (inicio: %s, final: %s, duracion: %s). Tiempos especificados por el usuario: inicio: %s, final %s" % (inicio, final, video.duracion, video.recorte_inicio, video.recorte_final)
#         video.save(skip_fecha_modificacion=True)
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

#     video = Video.objects.get(pk=video_pk)
#     video.archivo.save(os.path.basename(video.archivo.name), recortado_content, save=False)
#     video.procesado = False
#     video.duracion = duracion
#     video.observaciones = (video.observaciones or '') + "\nRecortado el %s por %s" % (datetime.datetime.now().strftime('%Y-%m-%d'), user.username if user else 'alguien')
#     video.save()

#     if video.archivo_subtitulado:
#         recomprimir(video.archivo_subtitulado.path)

#         video = Video.objects.get(pk=video_pk)
#         recortado_content = ContentFile(open(temp_mp4, 'r').read())
#         video.archivo_subtitulado.save(os.path.basename(video.archivo_subtitulado.name), recortado_content, save=False)
#         video.save()

#     video.resolucion = 0  # segmenta de nuevo
#     video.save()
#     os.remove(temp_mp4)

#     if user:
#         message = u'%s recortó video:\nhttp://captura-telesur.openmultimedia.biz/admin/videos/video/%s/\n\nArchivo recortado:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.username, video_pk, video.archivo.url)
#         do_send_mail('Video RECORTADO %s por %s' % (video_pk, user.username), message,
#             'captura@correo.tlsur.net', ['multimedia_edicion@correo.tlsur.net'],
#             fail_silently=False)

#         message = u'%s, el RECORTE del video %d que solicitaste ha finalizado.\n\nEl video es:\nhttp://captura-telesur.openmultimedia.biz/admin/videos/video/%s/\n\nArchivo de video:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.first_name, video_pk, video_pk, video.archivo.url)
#         do_send_mail(u'RECORTE de video %d finalizado' % video_pk, message,
#             'captura@correo.tlsur.net', [user.email],
#             fail_silently=True)


# def recortar_video(sender, **kwargs):
#     video = kwargs['instance']

#     if video.procesado() and (video.recorte_inicio or video.recorte_final):
#         try:
#             user = User.objects.get(username=video.usuario_modificacion)
#         except:
#             user = User()

#         job = recortar_video_job.delay(video.pk, video.archivo.path, video.recorte_inicio, video.recorte_final, video.duracion, user.pk)
#         video.recorte_inicio = None
#         video.recorte_final = None
#         video.save(skip_fecha_modificacion=True)

#         sleep(0.5)
#         if not job.is_started:
#             job.meta['retrasado'] = True
#             job.save()
#             message = u'%s, el RECORTE del video %d que solicitaste aún no ha comenzado porque está esperando en cola.' % (user.first_name, video.pk)
#             do_send_mail(u'RECORTE de video %d retrasado' % video.pk, message,
#                 'captura@correo.tlsur.net', [user.email],
#                 fail_silently=True)



# def segmentar_video(sender, **kwargs):
#     video = kwargs['instance']
#     if not video.resolucion:
#         r = redis.Redis('localhost', db=2)
#         key = 'segmentar-%d' % video.pk
#         if not r.get(key):
#             r.incr(key)
#             segmentar_video_job.delay(video.pk)





# def sprites(sender, **kwargs):
#     video = kwargs['instance']
#     if not video.sprites:
#         r = redis.Redis('localhost', db=2)
#         key = 'sprites-%d' % video.pk
#         if not r.get(key):
#             r.incr(key)
#             Video.objects.filter(pk=video.id).update(sprites=-1)
#             sprites_job.delay(video.pk)


# def delete_files(sender, **kwargs):
#     video = kwargs['instance']
#     file_attrs = ('archivo', 'imagen', 'audio', 'subtitulos')
#     for file_attr in file_attrs:
#         attr = getattr(video, file_attr)
#         if attr:
#             # archivo, audio and imagen may be shared in translated videos, dont delete them
#             if (video.video_original_id or video.traducciones.count()) and file_attr in ['archivo', 'audio', 'imagen']:
#                 return
#             else:
#                 attr.delete(save=False)
# post_delete.connect(delete_files, sender=Video)


# Connect model signal receivers

# post_save.connect(procesar_video, sender=Video)
# post_init.connect(reset_fps, sender=Video)
#post_save.connect(segmentar_video, sender=Video)
#post_save.connect(sprites, sender=Video)
# post_save.connect(recortar_video, sender=Video)
# post_save.connect(crear_traducciones, sender=Video)
# post_save.connect(generar_archivo_subtitulado, sender=Video)


