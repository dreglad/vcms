# -*- coding: utf-8 -*-
"""Video operations with FFmpeg"""
import json
import logging
import os
import re
import shutil
import wget

from django.conf import settings
from django.core.files.base import ContentFile
from subprocess import Popen, PIPE, call


logger = logging.getLogger('vcms.video_ops')


H264_PARAMS = {
    'profile': 'main',
    'level': '3.1',
    'crf': 22,
    'max_width': 2048,
    'audio_bitrate': 128,
    'audio_samplerate': 44100,
}

HLS_MODES = [  # must be ordered with highest height first
    {'height': 1080, 'cut_height': 800,     'profile': 'main',     'level': 32,
         'fps': 30,   'bandwidth': 3500000, 'bitrate': 3500,       'gop': 72 },

    { 'height': 720, 'cut_height': 600,     'profile': 'main',     'level': 32,
         'fps': 24,   'bandwidth': 2000000, 'bitrate': 1800,       'gop': 72 },

    { 'height': 480, 'cut_height': 400,     'profile': 'baseline', 'level': 31,
         'fps': 24,   'bandwidth': 1000000, 'bitrate': 900,        'gop': 72 },

    { 'height': 360, 'cut_height': 300,    'profile': 'baseline',  'level': 31,
         'fps': 24,   'bandwidth': 700000, 'bitrate': 600,         'gop': 72 },

    { 'height': 240, 'cut_height': 200,    'profile': 'baseline',  'level': 31,
         'fps': 12,   'bandwidth': 400000, 'bitrate': 320,         'gop': 36 },

    { 'height': 120, 'cut_height': 100,    'profile': 'baseline',  'level': 31,
         'fps': 12,   'bandwidth': 200000, 'bitrate': 180,         'gop': 36 },
]

HLS_PARAMS = {
    'time': 9,
    'list_size' : 0,
}


# TODO: WEBM/DASH
WEBM_PARAMS = {}  
DASH_MODES = []  
DASH_PARAMS = {}


VIDEO_EXTENSIONS = (
    '.3gp', '.asf', '.avi', '.avi', '.flv', '.mkv', '.mov', '.mp4', '.mpg',
    '.ogg', '.ogv', '.rm', '.swf', '.webm', '.wmv',
)



def get_video_stream_info(file):
    """Returns first video stream info dictionary, if any, using ffprobe"""
    cmd = 'ffprobe -v error -show_streams -print_format json %s' % file
    info = json.loads(Popen(cmd, shell=True, stdout=PIPE).stdout.read())
    logger.debug('Got video stream info: %s' % info)
    try:
        return [x for x in info['streams'] if x['codec_type'] == 'video'][0]
    except KeyError, IndexError:
        return {} # Didn't found any video streams in video_file


def get_video_info(file):
    """Returns dictionary with info about the video format, using ffprobe"""
    cmd = ('ffprobe -v error -print_format json -show_entries '
           'format=duration,size:stream=codec_name,width,height %s') % file
    info = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    logger.debug('Got video format info: %s' % info)
    return json.loads(info)


def get_video_autocrop_filter(input_file):
    """Returns measured recommended crop filter switch to get rid of black bars
    """
    cmd = ('ffmpeg -ss 10 -i {input} -t 1 -vf cropdetect -f null - 2>&1 | '
           'awk "/crop/ { print $NF }" | tail -1').format(input_file)
    autocrop = Popen(cmd, stdout=PIPE, shell=True).stdout.read()
    logger.debug('Got video autocrop value: %s' % autocrop)
    return '-vf "crop=%s"' % autocrop


def get_video_duration(input_file):
    """Returns a datetime.timedelta representing video duration"""
    cmd = ('ffmpeg -i {input_file} 2>&1 | grep "Duration" '
           '| cut -d " " -f 4 | cut -d "." -f 1').format(input=input_file)
    d = Popen(cmd, stdout=PIPE, shell=True).stdout.read().strip().split(':')
    logger.debug('Got video duration: %s' % d)
    return timedelta(hours=int(d[0]), minutes=int(d[1]), seconds=int(d[2]))


def extract_video_image(input_file, output_file, offset=-1, autocrop=True):
    """Extracts and optimizes video image at the specified offset (or auto)

    Keyword arguments:
    offset -- Offset in seconds or -1 to take it at the middle (default -1)
    autocrop -- Apply autocrop filter to get rid of black bars (default True)
    """
    if offset == -1:
        offset = abs(math.ceil(get_video_duration(input_file).seconds/2))
    crop_filter = ''
    if autocrop:
        crop_filter = '-vf "crop=%s"' % get_video_autocrop(input_file)
    cmd = ('ffmpeg -y -ss {offset} -i {input_file} -vframes 1 {crop_filter} '
           '-an {output_file}').format(
                input_file=input_file, output_file=output_file,
                offset=offset, crop_filter=crop_filter
                )
    logger.info('Extracting iamge with command: %s' % cmd)
    call(cmd, shell=True)
    cmd = ('convert -strip -interlace Plane -gaussian-blur 0.025 '
           '-quality 99% {img} {img}').format(img=img_file)
    logger.info('Optimizing iamge with command: %s' % cmd)
    return (call(cmd, shell=True) == 0)


def compress_h264mpeg4avc(imput_file, output_file, vstats_file, autocrop=True):
    """Compress to a normalized H264/MPEG-4 AVC video.

    Keyword arguments:
    vstats_file -- File path where to write progress stats (Default None)
    autocrop -- Whether or not to autocrop video to get rid of black bars
    """
    autocrop_filter = autocrop and get_video_autocrop_filter(input_file) or ''
    cmd = ('ffmpeg -y -vstats_file {vstats_file} -i {input_file} '
           '-c:a libfdk_aac -b:a {params[audio_bitrate]}k '
           '-ar {params[audio_samplerate]} -c:v libx264 -crf {params[crf]} '
           '-vf "scale=\'min(iw,{params[max_width]})\':-2" '
           '{autocrop_filter} -profile:v {profile} -level:v {level} '
           '-pix_fmt yuv420p -threads 0 -movflags +faststart {output_file}'
                ).format(input_file=input_file, output_file=output_file,
                         params=H264_PARAMS, autocrop_filter=autocrop_filter,
                         vstats_file=vstats_file or '/dev/null')
    logger.info('Compressing with command: %s' % cmd)
    return (call(cmd, shell=True) == 0)


def make_hls_segments(input_file, output_dir, progress_fn=None):
    """Make HLS segments and playlist

    Keyword arguments:
    progress_fn -- Called after each quality segmentarion has finished
    """
    logger.debug('Starting HLS segmentation for %s' % input_file)

    playlists = []

    # cleanup output directory (will delete any previous segments)
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)
    os.makedirs(hls_dir)

    # detemrine needed modes (different qualities)
    video_height = get_video_stream_info(input_file)['height']
    for max_mode in HLS_MODES:
        if video_height >= max_mode['cut_height']:
            # select maximum AND all lower modes
            modes = [m for m in HLS_MODES if m['height'] <= max_mode['height']]
            logger.info('Starting HLS segmentation, max_mode: %s' % max_mode)
            break
    
    # create segments for each mode, lowest first, so video can play sooner
    for mode in modes[::-1]:
        playlist_name = '{0}p.m3u8'.format(mode['height'])
        playlist_file = os.path.join(output_dir, playlist_name)
        # hls segmenting ffmpeg command, the key is the scalefilter -2:height
        cmd = ('ffmpeg -y -i {input_file} -c:a copy -strict experimental '
               '-c:v libx264 -pix_fmt yuv420p -profile:v {mode[profile]} '
               '-level {mode[level]} -b:v {mode[bitrate]}K -r {mode[fps]} '
               '-g {mode[gop]} -f hls -hls_time {hls_params[time]} '
               '-hls_list_size {hls_params[list_size]} '
               '-vf "scale=-2:{mode[height]}" -threads 0 {output_file}') \
                    .format(input_file=input_file, output_file=playlist_file,
                            mode=mode, hls_params=HLS_PARAMS)
        logger.info('Segmenting %s with command: %s' % (mode['height'], cmd))
        call(cmd, shell=True)

        # generate and append current playlist line of global playlist
        playlists.append((
            '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bandwidth},'
            'RESOLUTION={sream[width]}x{sream[height]}\n{mmplaylist}') \
                .format(bandwidth=mode['bandwidth'],
                        stream=get_video_stream_info(playlist_file),
                        playlist=os.path.basename(playlist_file))
            )
        # report progress
        progress_fn and progress_fn(
            playlist=playlist_name, current=mode['height'],
            total=max_mode['height']
            )
    # write global playlist
    with open(os.path.join(output_dir, 'playlist.m3u8'), 'w') as f:
        f.write("#EXTM3U\n" + "\n".join(playlists[::-1])) # reverse order again

    # finished
    progress_fn and progress_fn(playlist='playlist.m3u8')
    logger.debug('Finished HLS segmentation to %s' % output_file)
    return os.path.exists(os.path.join(output_dir, 'playlist.m3u8'))


def compress_dashavc264( input_file, output_file, vstats_file, autocrop=True):
    """Not implemented"""
    pass


def make_dash_segments():
    """not implemented"""
    pass


def download_video(source, output_file, progress_fn=None, force_direct=False):
    """Downloads video file from url and"""

    if os.path.isabs(source) and os.path.exists(source):
        # is a local file
        return shutil.copyfile(source, output_file)

    elif force_direct or source.endswith(VIDEO_EXTENSIONS):
        # is a direct download
        def wget_progress(current, total, width=80):
            if progress_fn: progress_fn(url, path, (current/float(total))*100)
        wget.download(src, path, bar=wget_progress)
        return os.path.exists(output_file)

    else:
        # is a you-get download
        p = Popen(['you-get', '--force',
                   '--output-dir', os.path.dirname(output_file),
                   '--output-filename', os.path.basename(output_file),
                   source], stdout=PIPE)
        if progress_fn:
            for line in iter(lambda: p.stdout.read(50), b''):
                m = re.match(r'.* (\d+\.\d+)%.*', line)
                if m: progress_fn(url, path, float(m.group(1)))
        p.communicate()
        return p.returncode == 0 and os.path.exists(path)
