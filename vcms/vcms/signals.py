# -*- coding: utf-8 -*-
import logging
import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from vcms.jobs.video import create_new_video_job
from videos.models import Video


logger = logging.getLogger('vcms')


@receiver(post_save, sender=Video)
def process_video(sender, **kwargs):
    video = kwargs['instance']

    if video.procesamiento == Video.PROCESAMIENTO.nuevo:
        logger.debug('post_save received to process new video: %s' % video)

        status_path = os.path.join(settings.TEMP_ROOT, 'status', video.uuid)
        with open(status_path, 'w') as status_file:
            status_file.write('queue')

        Video.objects.filter(pk=video.pk) \
            .update(procesamiento=Video.PROCESAMIENTO.procesando)

        logger.debug('About to delay create_new_video_job')
        create_new_video_job.delay(video.pk)
