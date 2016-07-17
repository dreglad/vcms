# -*- coding: utf-8 -*-
import logging
import math
import os
import shutil
from time import sleep

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django_rq import job
from PIL import Image

from vcms import makesprites, video_ops
from videos.models import Video


logger = logging.getLogger('vcms')


def _video_status_file(video, content=None):
    """Helper to write to video status file"""
    with open(os.path.join(settings.TEMP_ROOT, 'status', video.uuid),'w') as f:
        if content is not None:
            logger.debug('Writing "%s" to status file "%s"' % (content, f))
            return f.write(content)
        else:
            logger.debug('Created blank status file: %s' % f)


@job('low', timeout=2*3600)
def make_sprites_job(video_pk):
    TOTAL_SPRITES = 120  # total de 120 sprites

    connection.close() # force re-connnect to avoid DB tomeout issues
    video = Video.objects.get(pk=video_pk)

    # prepare
    sprites_dir = os.path.join(settings.MEDIA_ROOT, 'sprites', video.uuid)
    if os.path.isdir(sprites_dir):
        shutil.rmtree(sprites_dir)
        logger.info('Removed existing sprites directory: %s' % sprites_dir)
    os.makedirs(sprites_dir)

    # make sprites
    interval = math.ceil(video.duracion.total_seconds()/TOTAL_SPRITES)
    makesprites.run(makesprites.SpriteTask(
        videofile=video.archivo.path, outdir=sprites_dir
        ), thumbRate=interval)

    # update object
    Video.objects.filter(pk=video_pk).update(
        sprites=os.path.join('sprites', video.uuid, 's.vtt')
        )


@job('low', timeout=3*3600)
def make_hls_job(video_pk):
    connection.close() # force re-connnect to avoid DB tomeout issues
    video = Video.objects.get(pk=video_pk)
    #if video.resolucion == -1:
    #    return  # Being segmented right now (-1)
    #else:  # mark as currently being segmenting
    #    Video.objects.filter(pk=video_pk).update(resolucion=-1)

    def playlist_progress(playlist, current=None, total=None):
        """Called after each partial or the global playlist finises"""
        hls_uri = os.path.join('hls', video.uuid, playlist)

        if playlist == 'playlist.m3u8':
            Video.objects.filter(pk=video.pk).update(hls=hls_uri)
            logger.debug('Finished segmenting all video modes: %s' % hls_uri)
        else:
            Video.objects.filter(pk=video.pk) \
                .update(hls=hls_uri, resolucion=current, max_resolucion=total)
            logger.debug(('Finished partial playlist %s of height %d '
                          'out of %d ') % (hls_uri, current, total))
    # make HLS segments and playlists
    video_ops.make_hls_segments(
        input_file=video.archivo.path,
        output_dir=os.path.join(settings.MEDIA_ROOT, 'hls', video.uuid),
        progress_fn=playlist_progress
        )


@job('high', timeout=3600)
def create_new_video_job(video_pk):
    logger.info('Sarting create_new_video_job with video_pk: %d' % video_pk)

    connection.close();
    video = Video.objects.get(pk=video_pk)

    '''
    Download
    '''
    download_path = os.path.join(settings.TEMP_ROOT, 'original', video.uuid)
    source = video.origen_url or video.archivo_original or (video.archivo and video.archivo.path)
    logger.info('About to download %s to %s' % (source, download_path))
    cdn = '://cdn.' in source
    def progress_fn(source, destination, progress):
        _video_status_file(video, 'download %g' % progress)
    download = video_ops.download_video(source, download_path, force_direct=cdn,
                                        progress_fn=progress_fn)
    '''
    Validate
    '''
    try:
        if not download or not os.path.exists(download_path):
            raise AssertionError('1 No se pudo descargar archivo de video')

        stream_info = video_ops.get_video_stream_info(download_path)

        if not stream_info.get('codec_type') == 'video':
            raise AssertionError('2 El archivo obtenido no es un video válido')

        video_format_info = video_ops.get_video_info(download_path)['format']
        if not 'duration' in video_format_info:
            raise AssertionError('3 El archivo obtenido parece ser una imgaen, no un video')

        _video_status_file(video, 'valid %s' % video_format_info['duration'])

    except AssertionError as e:
        logger.error('Error validating download %s, error: %s' % (download, e))
        _video_status_file(video, 'error %s' % e)

        Video.objects.filter(pk=video.pk) \
            .update(procesamiento=Video.PROCESAMIENTO.error)
        return

    '''
    Data
    '''
    Video.objects.filter(pk=video.pk) \
        .update(duracion=video_ops.get_video_duration(download_path),
                original_metadata=stream_info)
    '''
    Image
    '''
    image_name = '%s.jpg' % video.uuid
    image_path = os.path.join(settings.TEMP_ROOT, 'img', image_name)

    video_ops.extract_video_image(download_path, image_path)
    img_size=Image.open(image_path).size

    video.imagen.save(image_name, # move file to target storage
        ContentFile(open(image_path).read()), save=False)
    os.remove(image_path)
    Video.objects.filter(pk=video.pk) \
        .update(imagen='images/%s' % image_name,
                width=img_size[0],
                height=img_size[1])
    '''
    Video
    '''
    video_name = '%s.mp4' % video.uuid
    video_path = os.path.join(settings.TEMP_ROOT, 'mp4', video_name)
    vstats_path = os.path.join(settings.TEMP_ROOT, 'vstats', video.uuid)

    video_ops.compress_h264mpeg4avc(download_path, video_path, vstats_path)

    video.archivo.save(video_name, # move file to target storage
        ContentFile(open(video_path).read()), save=False)
    os.remove(video_path)
    Video.objects.filter(pk=video.pk) \
        .update(archivo='videos/%s' % video_name,
                procesamiento=Video.PROCESAMIENTO.listo)

    # update status file
    _video_status_file(video, 'done %d' % video.pk)

    #cleanup
    os.remove(vstats_path)
    os.remove(download_path)

    # Launch subtasks for sprites and segments
    make_sprites_job.delay(video.pk)
    make_hls_job.delay(video.pk)


def error_handler(job, *exc_info):
    """Error hanfling"""
    video_pk = job.args[0]
    logger.error('Error executing job %s for %s' % (exc_info, video_pk))
    if job.func_name == make_hls_job.func_name:
        Video.objects.get(pk=video_pk).update(resolucion=0)
    elif job.func_name == create_new_video_job.func_name:
        Video.objects.get(pk=video_pk) \
            .update(procesamiento=Video.PROCESAMIENTO.error)
    return True  # continue with the next handler
