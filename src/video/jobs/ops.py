# -*- coding: utf-8 -*-
from django.db import connection
from django.core.files.base import ContentFile
from clips.models import *
from django.conf import settings
from subprocess import Popen, PIPE, call
import datetime
import time
import os
import re
import urllib
import json
import uuid
import shutil
from django_rq import job
from rq import get_current_job
from django.contrib.auth.models import User
from time import sleep
from django.core.mail import send_mail
import redis
from video.video_ops import *
from clips.models import Clip, TipoClip


@job('high', timeout=3600)
def crear_nuevo_clip_job(request_dict):
    print u"Peticion de nuevo clip con request: %s" % request_dict

    tmp_base = settings.STORAGE_DIR + 'temp'
    archivo_id = request_dict.get('archivo_id', request_dict.get('archivo'))
    descarga_path = '%s/descargado_%s' % (tmp_base, archivo_id)
    status_path = '%s/status/%s.txt' % (tmp_base, archivo_id)
    vstats_path = '%s/vstats_%s.txt' % (tmp_base, archivo_id)
    comprimido_path = '%s/comprimido_%s.mp4' % (tmp_base, archivo_id)

    if archivo_id.startswith('http'):
        url = archivo_id
    else:
        url = 'http://upload.openmultimedia.biz/files/%s' % archivo_id

    tries = 0
    while tries < 8:
        try:
            tries += 1
            # update status
            print u"Descargando archivo (intento %d): %s" % (tries, url)
            with open(status_path, 'w') as status_file:
                status_file.write('download %d' % tries)
            webfile = urllib2.urlopen(url)
            descargafile = open(descarga_path, 'w')
            descargafile.write(webfile.read())
            webfile.close()
            descargafile.close()
            break
        except Exception as e:
            print e
            continue

    # Archivo descargado, checar validez
    stream_info = get_video_stream_info(descarga_path)
    duration = stream_info.get('duration')

    with open(status_path, 'w') as status_file:
        if not stream_info or not duration:
            print u"Archivo invalido, temrinando"
            status_file.write('invalid')
            return
        else:
            print u"Archivo valido, video de duracion: %s" % duration
            status_file.write('valid %s' % duration)

    # compress
    ffmpeg_params = ' -c:a libfdk_aac -b:a 128k -ar 44100 -c:v libx264 -crf 22 -vf "scale=\'min(iw,1280)\':-2" -profile:v main -level:v 3.1 -pix_fmt yuv420p -threads 0'
    compress_cmd = 'ffmpeg -y -vstats_file %s -i %s %s -movflags +faststart %s' % (vstats_path, descarga_path, ffmpeg_params, comprimido_path)
    print u"Comprimiendo en: %s" % comprimido_path
    call(compress_cmd, shell=True)

    connection.close() # refresh connection

    tipo = request_dict.get('tipo')
    if tipo.isdigit():
        tipo = TipoClip.objects.get(pk=tipo)
    else:
        tipo = TipoClip.objects.get(slug=tipo)

    clip = Clip(
        duracion=datetime.time(0,0),
        tipo=tipo,
        fecha=datetime.datetime.now(),
        usuario_creacion = request_dict.get('usuario_remoto'),
        usuario_redaccion = request_dict.get('usuario_remoto'),
        titulo = request_dict.get('titulo'),
        descripcion = request_dict.get('descripcion'),
        observaciones = u"\nCreado desde Admin por %s con archivo_id: %s" % (request_dict.get('usuario_remoto'), archivo_id),
    )

    if request_dict.get('categoria'):
        clip.categoria = Categoria.objects.get(slug=request_dict.get('categoria'))
    if request_dict.get('programa'):
        clip.programa = Programa.objects.get(slug=request_dict.get('programa'))
    # if request_dict.get('tags'):
    #     clip.tags = request_dict.get('tags')
    if request_dict.get('hashtags'):
        clip.hashtags = request_dict.get('hashtags')
    if request_dict.get('corresponsal'):
        clip.corresponsal = Corresponsal.objects.filter(slug=request_dict.get('corresponsal'))[0]
    if request_dict.get('pais'):
        try:
            if request_dict.get('pais').isdigit():
                clip.pais = Pais.objects.get(pk=request_dict.get('pais'))
            else:
                clip.pais = Pais.objects.get(codigo=request_dict.get('pais'))
        except Pais.DoesNotExist:
            pass
    if request_dict.get('publicado') in ['1', 'true']:
        clip.publicado = True
    clip.seleccionado = request_dict.get('seleccionado') in ['1', 'true']

    print u"Guardando nuevo clip en base de datos"
    clip.archivo.save(u"video-%s.mp4" % datetime.datetime.now(), ContentFile(open(comprimido_path).read()), save=False)
    clip.save()

    with open(status_path, 'w') as status_file:
        status_file.write('done %d' % clip.pk)

    os.unlink(descarga_path)
    os.unlink(comprimido_path)
    os.unlink(vstats_path)

    print u"FIN"


@job('low', timeout=3600)
def sprites_job(clip_pk):
    from video import makesprites

    connection.close()
    try:
        clip = Clip.objects.get(pk=clip_pk)
    except Clip.DoesNotExist:
        return

    if clip.duracion < datetime.time(0, 2):
        interval = 1
    if clip.duracion < datetime.time(0, 10):
        interval = 2
    elif clip.duracion < datetime.time(0, 20):
        interval = 10
    elif clip.duracion < datetime.time(0, 30):
        interval = 35
    else:
        interval = 45

    # Create or empty directory
    basedir = '%ssprites/%d' % (settings.STORAGE_DIR, clip.pk)
    if os.path.isdir(basedir):
        shutil.rmtree(basedir)
    os.makedirs(basedir)

    sprites = makesprites.SpriteTask(videofile=clip.archivo.path, outdir=basedir)
    makesprites.run(sprites, thumbRate=interval)

    # Finish
    Clip.objects.filter(pk=clip_pk).update(sprites=interval)



@job('low', timeout=3*3600)
def segmentar_video_job(clip_pk):
    connection.close()

    try:
        clip = Clip.objects.get(pk=clip_pk)
    except Clip.DoesNotExist:
        return

    # already segmented (>0) or being segmented right now (-1)
    if clip.resolucion or clip.resolucion == -1:
        return
    else:
        # mark as currently being segmenting
        Clip.objects.filter(pk=clip_pk).update(resolucion=-1)

    MODES = (
        # larger modes first
        {'height': 1080, 'cut_height': 900, 'bitrate': 3500, 'fps': 30, 'gop': 72, 'profile': 'main',     'level': 32, 'bandwidth': 3500000},
        {'height': 720,  'cut_height': 600, 'bitrate': 1800, 'fps': 24, 'gop': 72, 'profile': 'main',     'level': 32, 'bandwidth': 2000000},
        {'height': 480,  'cut_height': 400, 'bitrate': 900,  'fps': 24, 'gop': 72, 'profile': 'baseline', 'level': 31, 'bandwidth': 1000000},
        {'height': 360,  'cut_height': 300, 'bitrate': 600,  'fps': 24, 'gop': 72, 'profile': 'baseline', 'level': 31, 'bandwidth': 700000},
        {'height': 240,  'cut_height': 200, 'bitrate': 320,  'fps': 12, 'gop': 36, 'profile': 'baseline', 'level': 31, 'bandwidth': 400000},
        {'height': 120,  'cut_height': 100, 'bitrate': 180,  'fps': 12, 'gop': 36, 'profile': 'baseline', 'level': 31, 'bandwidth': 200000},
    )

    # select current AND all lower modes
    video_height = get_video_stream_info(clip.archivo.path)['height']
    for m in MODES:
        if video_height > m['cut_height']:
            modes = filter(lambda x: x['height'] <= m['height'], MODES)
            break

    # create M3U playlist
    playlist = "#EXTM3U\n"

    # create basedir if necessary
    archivo = clip.archivo
    basedir = '%shls/%d' % (settings.STORAGE_DIR, clip.pk)
    if os.path.isdir(basedir):
        shutil.rmtree(basedir)
    os.makedirs(basedir)

    # encode each mode and add them to the playlist
    for mode in modes:
        path = '%s/%dp.m3u8' % (basedir, mode['height'])

        # hls segmenting ffmpeg command, the key is the scalefilter -2:height
        cmd = ('ffmpeg -y -i %s -c:a copy -strict experimental -c:v libx264 '
               '-pix_fmt yuv420p -profile:v %s -level %s -b:v %sK -r %s -g %s '
               '-f hls -hls_time 9 -hls_list_size 0 -vf "scale=-2:%s" -threads 0 %s') % (
                   archivo.path,
                   mode['profile'], mode['level'],
                   mode['bitrate'], mode['fps'], mode['gop'],
                   mode['height'], path)
        call(cmd, shell=True)

        # verify file + extract width info for playlist
        video_stream = get_video_stream_info(path)

        playlist += "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=%d,RESOLUTION=%dx%d\n" % (mode['bandwidth'], video_stream['width'], video_stream['height'])
        playlist += "%s\n" % os.path.basename(path)

    # wite playlist
    file('%s/playlist.m3u8' % basedir, 'w').write(playlist)

    # Finish
    connection.close()
    Clip.objects.filter(pk=clip_pk).update(resolucion=modes[0]['height'])

# @job('subtitulaje', timeout=2*3600)
# def generar_archivo_subtitulado_job(clip_pk, archivo_path, srt_path, user_pk):
#     connection.close()

#     job = get_current_job()
#     try:
#         user = User.objects.get(pk=user_pk)
#     except:
#         user = User()

#     if 'retrasado' in job.meta and user:
#         del job.meta['retrasado']
#         job.save()
#         message = u'%s, el SUBTITULAJE del clip %d que solicitaste y estaba en cola acaba de comenzar.' % (user.first_name, clip_pk)
#         do_send_mail(u'SUBTITULAJE de clip %d comenzado' % clip_pk, message,
#            'captura@correo.tlsur.net', [user.email],
#            fail_silently=True)

#     # Sólo para clips ya procesados y si tienen subtitulos pero aún no archivo_subtitulado
#     temp_avi = '/mnt/captura-media/temp/subtitulado-mencoder-%s.avi' % clip_pk
#     temp_mp4 = '/mnt/captura-media/temp/subtitulado-%s.mp4' % clip_pk

#     insertar_subtitulos = 'mencoder -oac pcm -ovc lavc -lavcopts vbitrate=5000:threads=4 -ofps 30 -subfont-text-scale 2 -sub-bg-color 0 -sub-bg-alpha 255 -spuaa 4 -ass -ass-color FFFF0000 -ass-font-scale 2 -subpos 80 '
#     insertar_subtitulos+= '-utf8 -sub "%s" -o "%s" "%s"' % (srt_path, temp_avi, archivo_path)
#     print 'Ejecutando comando: %s' % insertar_subtitulos
#     call(insertar_subtitulos, shell=True)

#     recomprimir_video = 'ffmpeg -y -i %s -c:a libfdk_aac ' % temp_avi
#     recomprimir_video += '-c:v libx264 -strict -2 -profile:v main -level:v 3.1 -threads 0 -movflags faststart %s' % temp_mp4
#     # recomprimir_video += '-vcodec libx264 -vpre baseline -b 512k -flags +loop+mv4 -cmp 256 '
#     #recomprimir_video += '-vcodec libx264 -profile:v baseline -flags +loop+mv4 -cmp 256 '
#     #recomprimir_video += '-partitions +parti4x4+parti8x8+partp4x4+partp8x8+partb8x8 -me_method hex -subq 7 '
#     #recomprimir_video += '-trellis 1 -refs 5 -bf 0 -coder 0 -me_range 16 -g 250 -keyint_min 25 '
#     #recomprimir_video += '-sc_threshold 40 -i_qfactor 0.71 -qmin 10 -qmax 51 -qdiff 4 -strict -2 -threads 0 -movflags faststart %s' % temp_mp4
#     call(recomprimir_video, shell=True)
#     #call('/usr/bin/mp4file --optimize %s' % temp_mp4, shell=True)

#     subtitulado_content = ContentFile(open(temp_mp4, 'r').read())

#     try:
#         clip = Clip.objects.get(pk=clip_pk)
#         clip.archivo_subtitulado.save(u'subtitulado-%s.mp4' % clip.pk, subtitulado_content, save=False)
#         clip.transferido = False
#         clip.observaciones = ''
#         clip.resolucion = 0
#         clip.save()

#         try:
#             os.remove(temp_avi)
#             os.remove(temp_mp4)
#         except OSError:
#             pass

#         if user:
#             message = u'%s generó clip subtitulado:\n http://captura-telesur.openmultimedia.biz/admin/clips/clip/%s/\n\nArchivo subtitulado:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.username, clip_pk, clip.archivo_subtitulado.url)
#             do_send_mail(u'Clip SUBTITULADO %s por %s' % (clip_pk, user.username), message,
#                 'captura@correo.tlsur.net', ['multimedia_edicion@correo.tlsur.net'],
#                 fail_silently=False)

#             message = u'%s, el SUBTITULAJE del clip que solicitaste está listo.\n\nEl clip es:\nhttp://captura-telesur.openmultimedia.biz/admin/clips/clip/%s/\n\nArchivo subtitulado:\nhttp://captura-telesur.openmultimedia.biz%s' % (user.first_name, clip_pk, clip.archivo_subtitulado.url)
#             do_send_mail(u'SUBTITULAJE de clip %d listo.' % clip_pk, message,
#                 'captura@correo.tlsur.net', [user.email],
#                 fail_silently=True)

#     except Clip.DoesNotExist:
#         raise Clip.DoesNotExist

