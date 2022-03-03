import os
import re
from subprocess import (
    PIPE,
    Popen,
)

FFMPEG_ARGS = {
    'vcodec': 'libx265',
    'crf': 28,
}

EXTS_INFO = {
    'mp4': ['mp4', 'm4v'],
    'mov': ['mov', 'qt'],
    'avi': ['avi'],
    'flv': ['flv'],
    'wmv': ['wmv', 'asf'],
    'mpeg': ['mpeg', 'mpg', 'vob'],
    'mkv': ['mkv'],
}


def _prepare(s):
    match = re.match(r'^[a-zA-Z0-9\-\"/\.\'\ \\_]*$', s)

    if not match:
        raise OSError('Invalid argument `%s`' % s)

    return match.group(0)


def get_video_type(path_or_filename):
    _ext = os.path.basename(path_or_filename).split('.')[-1]

    for vtype, file_ext in EXTS_INFO.items():
        if _ext.lower() in file_ext:
            return vtype

    raise VideoError('Unknown file extension `%s`' % _ext)


class VideoError(Exception):
    pass


class Video:
    ext = ''
    ext_info = {}
    command = ''

    def __init__(self, path, preset='ultrafast') -> None:
        self.path = _prepare(path)

        if not self.path:
            raise VideoError(f'Invalid source file {path}.')

        self.ext = get_video_type(self.path)

    def get_command(self, dst: str, **kwargs):
        dest = _prepare(dst)

        if not dest:
            raise VideoError(f'Invalid destination file {dst}.')

        self.command = command = (
            f'ffmpeg -i "{self.path}" -vcodec {FFMPEG_ARGS["vcodec"]} '
            f'-preset {_prepare(kwargs.get("preset", "ultrafast"))} '
            f'-crf {FFMPEG_ARGS["crf"]} "{dest}"'
        )
        return command

    def convert(self, dst: str):
        if not self.command:
            self.get_command(dst)

        process = Popen(self.command, shell=True, stdout=PIPE)

        return process.communicate()[0]
