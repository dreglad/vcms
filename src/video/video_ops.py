# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from django.conf import settings
from subprocess import Popen, PIPE, call
from fractions import Fraction
import wget
import json
import os
import re

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


def download_video(url, path, progress_fn=None):
    if any(url.find('openmultimedia.biz') != '-1',
           url.endswith(('.mp4', '.flv', '.mpg', '.webm', '.avi', '.mov'))):
        # direct download
        def wget_progress(current, total, width=80):
            if progress_fn: progress_fn(url, path, (current/float(total))*100)
        wget.download(url, path, bar=wget_progress)
        return os.path.exists(path)
    else:  # you-get download
        p = Popen(['you-get', '--force',
                   '--output-dir', os.path.dirname(path),
                   '--output-filename', os.path.basename(path),
                   url,
                ], stdout=PIPE)
        if progress_fn:
            for line in iter(lambda: p.stdout.read(50), b''):
                m = re.match(r'.* (\d+\.\d+)%.*', line)
                if m: progress_fn(url, path, float(m.group(1)))
        p.communicate()
        return p.returncode == 0 and os.path.exists(path)
