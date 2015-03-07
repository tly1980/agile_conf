#!/usr/bin/env python
from setuptools import setup, find_packages
import json
import os


def read(fname):
    with open(fname) as f:
        return f.read()


def load_version():
    with open('src/agile_conf/VERSION.txt') as f:
        return f.read().strip()


setup(
    name='agile_conf',
    version=load_version(),
    description='An async http client with keep-alive capabilities',
    long_description=read('README.txt'),
    license='BSD',
    author='Tom Tang',
    author_email='tly1980@gmail.com',
    url="https://github.com/tly1980/agile_conf",
    platforms='any',
    install_requires=[
        'PyYAML>=3.0',
        'Jinja2',
        'docopt>=0.6.2'
    ],
    scripts=['scripts/agc', 'scripts/shortcuts.sh'],
    package_dir={'': 'src'},
    packages=['agile_conf'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators'
    ],
)
