# -*- coding: utf-8 -*-
"""
vcms jobs - crear_nuevo, sprites, segmentar
"""
from datetime import timedelta
import math
import os
import shutil
from subprocess import Popen, PIPE, call
from time import sleep

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django_rq import job

from vcms.video_ops import download_video, get_video_info, get_video_stream_info
from videos.models import Video


@job('low', timeout=2*3600)
def sprites_job(video_pk):
    from vcms import makesprites
    print(u"Peticion de sprites video")
    connection.close()
    TOTAL_SPRITES = 120  # total de 120 sprites

    video = Video.objects.get(pk=video_pk)

    # preparar directorio de sprites
    sprites_dir = os.path.join(settings.MEDIA_ROOT, 'sprites', video.uuid)
    if os.path.isdir(sprites_dir):
        shutil.rmtree(sprites_dir)
    os.makedirs(sprites_dir)

    sprites = makesprites.SpriteTask(videofile=video.archivo.path,
                                     outdir=sprites_dir)
    interval = math.ceil(video.duracion.total_seconds()/TOTAL_SPRITES)
    makesprites.run(sprites, thumbRate=interval)

    # Actualiza BD
    Video.objects.filter(pk=video_pk) \
                 .update(sprites=os.path.join('sprites', video.uuid, 's.vtt'))


@job('low', timeout=3*3600)
def segmentar_video_job(video_pk):
    connection.close()
    video = Video.objects.get(pk=video_pk)
    if video.resolucion or video.resolucion == -1:
        return  # already segmented (>0) or being segmented right now (-1)
    else:  # mark as currently being segmenting
        Video.objects.filter(pk=video_pk).update(resolucion=-1)

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
    video_height = get_video_stream_info(video.archivo.path)['height']
    for m in MODES:
        if video_height > m['cut_height']:
            modes = filter(lambda x: x['height'] <= m['height'], MODES)
            break

    '''
    HLS
    '''
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', video.uuid)
    if os.path.isdir(hls_dir): shutil.rmtree(hls_dir)
    os.makedirs(hls_dir)

    playlists = []
    # encode each mode and add them to the playlist
    for mode in modes[::-1]:  # lowest quality first, so video can play sooner
        playlist_name = '{0}p.m3u8'.format(mode['height'])
        playlist_path = os.path.join(hls_dir, playlist_name)
        # hls segmenting ffmpeg command, the key is the scalefilter -2:height
        cmd = ('ffmpeg -y -i {input} -c:a copy -strict experimental ' \
               '-c:v libx264 -pix_fmt yuv420p -profile:v {profile} ' \
               '-level {level} -b:v {bitrate}K -r {fps} -g {gop} ' \
               '-f hls -hls_time 9 -hls_list_size 0 -vf "scale=-2:{height}" ' \
               '-threads 0 {output}').format(
                    input=video.archivo.path, profile=mode['profile'],
                    level=mode['level'], bitrate=mode['bitrate'],
                    height=min(mode['height'], video_height),
                    fps=mode['fps'], gop=mode['gop'], output=playlist_path)
        call(cmd, shell=True)
        # verify file + extract width info for playlist
        video_stream = get_video_stream_info(playlist_path)

        # save current playlist so far
        Video.objects.filter(pk=video.pk) \
                .update(hls=os.path.join('hls', video.uuid, playlist_name))

        # generate and append current playlist line of global playlist
        playlists.append('#EXT-X-STREAM-INF:PROGRAM-ID=1,' \
                         'BANDWIDTH={bandwidth},RESOLUTION=' \
                         '{video_stream[width]}x{video_stream[height]}' \
                         '\n{playlist_uri}'.format(
                                bandwidth=mode['bandwidth'],
                                video_stream=video_stream,
                                playlist_uri=os.path.basename(playlist_path)))

    
    # write global playlist
    with open(os.path.join(hls_dir, 'playlist.m3u8'), 'w') as f:
        f.write("#EXTM3U\n" + "\n".join(playlists[::-1]))

    # update resolucion and global playlist
    Video.objects.filter(pk=video.pk) \
                  .update(resolucion=min(mode['height'], video_height),
                          hls=os.path.join('hls', video.uuid, 'playlist.m3u8'))

    print('Fin segmentar')



@job('high', timeout=3600)
def crear_nuevo_video_job(video_pk):
    print(u"Peticion de nuevo video")
    connection.close();sleep(2)

    video = Video.objects.get(pk=video_pk)
    status_path = os.path.join(settings.TEMP_ROOT, 'status', video.uuid)

    '''
    Descarga
    '''
    descarga_path = os.path.join(settings.TEMP_ROOT, 'original', video.uuid)
    url = video.origen_url or video.archivo_original.replace('https', 'http')
    print('About to download "%s" to "%s"' % (url, descarga_path))
    def progress(url, path, progress):
        with open(status_path, 'w') as status_file:
            status_file.write('download %g' % progress)
    download = download_video(url, descarga_path, progress_fn=progress)

    '''
    Validación
    '''
    try:
        if not download or not os.path.exists(descarga_path):
            raise AssertionError('1 No se pudo descargar archivo de video')

        stream_info = get_video_stream_info(descarga_path)

        if not stream_info.get('codec_type') == 'video':
            raise AssertionError('2 El archivo obtenido no es un video válido')

        video_format_info = get_video_info(descarga_path)['format']
        if not 'duration' in video_format_info:
            raise AssertionError('3 El archivo obtenido parece ser una imgaen, no un video')

        with open(status_path, 'w') as status_file:
            status_file.write('valid %s' % video_format_info['duration'])

    except AssertionError as e:
        print('Failed: %s' % e)
        with open(status_path, 'w') as status_file:
            status_file.write('error %s' % e)
        Video.objects.filter(pk=video.pk) \
                     .update(procesamiento=Video.PROCESAMIENTO.error)
        return
    
    '''
    Diuracion y dimensiones
    '''
    ffcmd = 'ffmpeg -i {input} 2>&1 | grep "Duration" | cut -d " " -f 4 | ' \
            'cut -d "." -f 1'.format(input=descarga_path)
    dur = [int(x) for x in Popen(ffcmd, stdout=PIPE, shell=True)\
             .stdout.read().strip().split(':')]
    duracion = timedelta(hours=dur[0], minutes=int(dur[1]), seconds=dur[2])
    Video.objects.filter(pk=video.pk) \
                  .update(duracion=duracion,
                          original_width=stream_info['width'],
                          original_height=stream_info['height'],
                          original_metadata=stream_info)

    '''
    Imagen
    '''
    nombre_imagen = '{0}.jpg'.format(video.uuid)
    img_path = os.path.join(settings.TEMP_ROOT, 'img', nombre_imagen)
    ffcmd = 'ffmpeg -y -ss {offset} -i {descarga_path} -vframes 1 ' \
             '-an {img} '.format(offset=abs(math.ceil(duracion.seconds/2)),
                                 descarga_path=descarga_path, img=img_path)
    convertcmd = 'convert -strip -interlace Plane -gaussian-blur 0.025 ' \
                 '-quality 99% {img} {img}'.format(img=img_path)
    call(ffcmd, shell=True)
    call(convertcmd, shell=True)

    img_content = ContentFile(open(img_path).read())
    video.imagen.save(nombre_imagen, img_content, save=False)
    Video.objects.filter(pk=video.pk) \
                 .update(imagen='images/{0}'.format(nombre_imagen))
    os.remove(img_path)

    '''
    Compresión
    '''
    nombre_video = '{0}.mp4'.format(video.uuid)
    vstats_path = os.path.join(settings.TEMP_ROOT, 'vstats', video.uuid)
    mp4_path = os.path.join(settings.TEMP_ROOT, 'mp4', nombre_video)
    ffcmd = 'ffmpeg -y -vstats_file {vstats_path} -i {descarga_path} ' \
            '-c:a libfdk_aac -b:a {audio_bitrate}k -ar {audio_samplerate} ' \
            '-c:v libx264 -crf {crf} -vf "scale=\'min(iw,{max_width})\':-2" ' \
            '-profile:v {profile} -level:v {level} -pix_fmt yuv420p ' \
            '-threads 0 -movflags +faststart {mp4_path}'.format(
                    crf=22, max_width=2048, audio_bitrate=128,
                    audio_samplerate=44100, profile='main', level='3.1',
                    vstats_path=vstats_path, mp4_path=mp4_path,
                    descarga_path=descarga_path)
    print(u"Comprimiendo con comando: %s" % ffcmd)
    call(ffcmd, shell=True)
    mp4_content = ContentFile(open(mp4_path).read())
    video.archivo.save(nombre_video, mp4_content, save=False)
    Video.objects.filter(pk=video.pk) \
                 .update(archivo='videos/{0}'.format(nombre_video),
                         procesamiento=Video.PROCESAMIENTO.listo)
    os.remove(mp4_path)

    with open(status_path, 'w') as status_file:
        status_file.write('done %d' % video.pk)
    os.remove(vstats_path)
    os.remove(descarga_path)

    # Segments and sprites
    sprites_job.delay(video.pk)
    segmentar_video_job.delay(video.pk)

    print(u"FIN")


def error_handler(job, exc_type, exc_value, traceback):
    video_pk = job.args[0]
    if job.func_name == segmentar_video_job.func_name:
        Video.objects.get(pk=video_pk).update(resolucion=0)
    elif job.func_name == crear_nuevo_video_job.func_name:
        Video.objects.get(pk=video_pk) \
                     .update(procesamiento=Video.PROCESAMIENTO.error)
    return False