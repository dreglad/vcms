# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from django.conf import settings
from subprocess import Popen, PIPE, call
from fractions import Fraction
import json

def get_video_stream_info(path):
    """Get video stream info dictionary using ffprobe"""
    cmd = 'ffprobe -v error -show_streams -print_format json %s' % path
    info = json.loads(Popen(cmd, shell=True, stdout=PIPE).stdout.read())
    try:
        return filter(lambda x: x['codec_type'] == 'video', info['streams'])[0]
    except KeyError:
        return {}

def get_video_aspect_ratio(video_stream_info):
    fraction = Fraction(video_stream_info.get('width'), video_stream_info.get('height'))
    return u'%d:%d' % (fraction.numerator, fraction.denominator)
