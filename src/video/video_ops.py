# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from django.conf import settings
from subprocess import Popen, PIPE, call
import json

def get_video_stream_info(path):
    """Get video stream info dictionary using ffprobe"""
    cmd = 'ffprobe -v error -show_streams -print_format json %s' % path
    info = json.loads(Popen(cmd, shell=True, stdout=PIPE).stdout.read())
    try:
        return filter(lambda x: x['codec_type'] == 'video', info['streams'])[0]
    except KeyError:
        return {}
