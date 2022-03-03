"""videoconverter.cli module -- Command Line Interface (CLI).

This module is designed to be used with the cli script (`bin/pyvideoc`).
Its purpose is to provide end user an easy to use command to convert videos.
"""

import concurrent.futures
import glob
import logging
import ntpath
import os
import re

import argparse

from pyvideoconverter.video import Video
from pyvideoconverter.parallel import SubprocessPool


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Convert videos from a file format to another.')

    parser.add_argument('-i', '--input', nargs='+', help='input files')
    parser.add_argument('-R', '--recursive', help='dir,extension of inputs')
    parser.add_argument(
        '-o', '--output', help='output filename format (with extension)', required=True)
    parser.add_argument(
        '--remove-source', help='Remove source(s). Use it carefully.', action="store_true")
    parser.add_argument('-s', '--speedup',
                        help='Number of threads to use.', type=int, default=10)
    parser.add_argument('-p', '--preset', help='Compression ratio / encoding speed.', choices=[
        'ultrafast', 'superfast', 'veryfast', 'faster', 'fast',
        'medium', 'slow', 'slower', 'veryslow'
    ], default='ultrafast')
    return parser


def is_f_str(s: str):
    return bool(re.match(r"^f'.*'$", s) or re.match(r'^f".*"$', s))


def get_dir(path: str):
    if os.path.sep not in path:
        return '.'
    return os.path.sep.join(path.split(os.path.sep)[0:-1])


def get_dynamic_argument(argument: str, variables: dict) -> str:
    return eval(argument, dict(
        __builtins__=None,
        **variables
    ))


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class CliConverter:
    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    def parse(self):
        _parser = _get_parser()
        self.args = _parser.parse_args()

        if self.args.input and self.args.recursive:
            _parser.error('Cannot use both `--input/-i` and `--recursive`.')

        if self.args.recursive:
            self.get_recursive_inputs()
        else:
            self.inputs = self.args.input

        if not is_f_str(self.args.output):
            self.args.output = "f'%s'" % self.args.output

        self.get_outputs()

    def get_recursive_inputs(self):
        self.inputs = glob.glob(self.args.recursive, recursive=True)

    def get_outputs(self):
        outputs = list()

        for input in self.inputs:
            input_filename = f = path_leaf(input)
            input_rawname = r = input_filename.split('.')[0]
            input_dir = d = get_dir(input)

            output = get_dynamic_argument(self.args.output, {
                'input_filename': input_filename,
                'input_rawname': input_rawname,
                'input_dir': input_dir,
                'f': f, 'r': r, 'd': d
            })

            outputs.append(output)

        self.outputs = outputs

    def proceed(self):
        inputs = self.inputs
        outputs = self.outputs
        commands = list()

        for input, output in zip(inputs, outputs):
            v = Video(input, preset=self.args.preset)
            commands.append(v.get_command(dst=output))

        with SubprocessPool(max_workers=self.args.speedup) as executor:
            futures = list()

            for command in commands:
                print(command)
                futures.append(executor.submit(command))

            for future in concurrent.futures.as_completed(futures):
                future.result()  # TODO: Handle results.

        if self.args.remove_source:
            for file in inputs:
                os.remove(file)

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, ags):

        if (ags.remove_source):
            self.log.warning('Please use `remove-source` carefully.')

        self._args = ags
