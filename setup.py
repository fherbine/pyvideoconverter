import os
import re
from setuptools import setup, find_packages

PKG_NAME='videoconverter'
PKG_DESC = 'Video converter developped in Python3.'

with open('requirements.txt') as reqf:
    requirements = reqf.read().splitlines()

_VFILE = os.path.join('src', PKG_NAME, '_version.py')

with open(_VFILE, 'rt') as vf:
    vline = vf.read()
    vregex = r'^__version__ = [\'"]([^\'"]*)[\'"]$'
    match = re.search(vregex, vline, re.M)

    if not match:
        raise RuntimeError('Unable to find version string in %s' % _VFILE)
    
    version = match.group(1)


setup(
    name=PKG_NAME, version=version, description=PKG_DESC,
    author='Félix HERBINET', author_email='fherbine@student.42.fr',
    license='', platforms='any', url='https://github.com/fherbine/%s' % PKG_NAME,
    package_dir={'': 'src'}, packages=find_packages('src'),
    include_package_data=True, requires=requirements, setup_requires=['wheel']
)