# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django_rq import job
from subprocess import Popen, PIPE, call
from clips.models import *
from video.video_ops import *
import datetime
import os
import shutil


@job('high', timeout=3600)
def crear_nuevo_clip_job(request_dict, uid):
    print(u"Peticion de nuevo clip con uid '%s' y request: '%s'" % (uid, request_dict))

    url = request_dict.get('url')
    origen = request_dict.get('origen')
    tmp_base = '%stemp' % settings.STORAGE_DIR
    descarga_path = '%s/descargado_%s' % (tmp_base, uid)
    status_path = '%s/status/%s.txt' % (tmp_base, uid)
    vstats_path = '%s/vstats_%s.txt' % (tmp_base, uid)
    comprimido_path = '%s/comprimido_%s.mp4' % (tmp_base, uid)

    if origen == 'upload':
        url = 'http://upload.openmultimedia.biz/files/%s' % url

    def progress(url, path, progress):
        with open(status_path, 'w') as status_file:
            status_file.write('download %g' % progress)

    print("About to download '%s' to '%s'" % (url, descarga_path))
    if download_video(url, descarga_path, progress_fn=progress):
        stream_info = get_video_stream_info(descarga_path)
        if stream_info.get('duration'):
            print("Donwnloaded valid file")
            with open(status_path, 'w') as status_file:
                status_file.write('valid %s' % stream_info.get('duration'))
        else:
            print('Downloaded but invalid file')
            with open(status_path, 'w') as status_file:
                status_file.write('invalid')
            os.unlink(descarga_path)
            return
    else:
        print('Download failed')
        with open(status_path, 'w') as status_file:
            status_file.write('invalid')
        return

    # compress
    ffmpeg_params = ' -c:a libfdk_aac -b:a 128k -ar 44100 -c:v libx264 -crf 22 -vf "scale=\'min(iw,2048)\':-2" -profile:v main -level:v 3.1 -pix_fmt yuv420p -threads 0'
    compress_cmd = 'ffmpeg -y -vstats_file %s -i %s %s -movflags +faststart %s' % (vstats_path, descarga_path, ffmpeg_params, comprimido_path)
    print(u"Comprimiendo en: %s" % comprimido_path)
    call(compress_cmd, shell=True)

    connection.close() # refresh connection

    clip = Clip(
        tipo=TipoClip.objects.get(slug=request_dict.get('tipo', 'noticia')),
        duracion=datetime.time(0,0),
        aspect=get_video_aspect_ratio(stream_info),
        fecha=datetime.datetime.now(),
        usuario_creacion = request_dict.get('usuario_remoto'),
        usuario_redaccion = request_dict.get('usuario_remoto'),
        titulo = request_dict.get('titulo'),
        descripcion = request_dict.get('descripcion'),
        observaciones = u"\nCreado desde Admin por %s con origen: %s, URL: %s" % (request_dict.get('usuario_remoto'), origen, url),
        hashtags = request_dict.get('hashtags'),
        seleccionado = request_dict.get('seleccionado') in ['1', 'true'],
        publicado = request_dict.get('publicado') in ['1', 'true']
    )
    if request_dict.get('categoria'):
        clip.categoria = Categoria.objects.get(slug=request_dict.get('categoria'))
    if request_dict.get('programa'):
        clip.programa = Programa.objects.get(slug=request_dict.get('programa'))
    if request_dict.get('corresponsal'):
        clip.corresponsal = Corresponsal.objects.filter(slug=request_dict.get('corresponsal'))[0]
    if request_dict.get('pais'):
        clip.pais = Pais.objects.get(pk=request_dict.get('pais'))

    print(u"Guardando nuevo clip en base de datos")
    clip.archivo.save(u"video-%s.mp4" % datetime.datetime.now(), ContentFile(open(comprimido_path).read()), save=False)
    clip.save()

    with open(status_path, 'w') as status_file:
        status_file.write('done %d' % clip.pk)

    os.unlink(descarga_path)
    os.unlink(comprimido_path)
    os.unlink(vstats_path)

    print(u"FIN")


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
        {'height': 1080, 'cut_height': 800, 'bitrate': 3500, 'fps': 30, 'gop': 72, 'profile': 'main',     'level': 32, 'bandwidth': 3500000},
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
                   min(mode['height'], video_height), path)
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
