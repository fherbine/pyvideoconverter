from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen, PIPE


class SubprocessPool(ThreadPoolExecutor):
    def _call(self, command):
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        return process.communicate()[0]

    def submit(self, command):
        return super().submit(self._call, command=command)
