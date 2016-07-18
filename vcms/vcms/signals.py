# -*- coding: utf-8 -*-
import logging
import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from vcms.jobs import create_new_video_job
from videos.models import Video


logger = logging.getLogger('vcms')


@receiver(post_save, sender=Video)
def process_video(sender, **kwargs):
    logger.debug('process_video | sender: %s; kwargs: %s' % (sender, kwargs))
    video = kwargs['instance']

    if video.procesamiento == Video.PROCESAMIENTO.nuevo:
        logger.debug('New video needs processing: %s' % video)

        status_path = os.path.join(settings.TEMP_ROOT, 'status', video.uuid)
        with open(status_path, 'w') as status_file:
            status_file.write('queue')
            logger.debug('Marked video as queued for processing: %s' % video)

        video.procesamiento = Video.PROCESAMIENTO.procesando
        video.save()

        create_new_video_job.delay(video.pk)
        logger.debug('create_new_video_job launched with %d' % video.pk)
