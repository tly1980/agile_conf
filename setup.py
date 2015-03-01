#!/usr/bin/env python
from setuptools import setup
import json
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def load_version():
    return '0.1'


setup(
    name='agile_conf',
    version=load_version(),
    description='An async http client with keep-alive capabilities',
    long_description=read('README.rst'),
    license='BSD',
    author='Tom Tang',
    author_email='tly1980@gmail.com',
    url="https://github.com/tly1980/agile_conf",
    platforms='any',
    install_requires=[
        'PyYAML>=3.0',
        'Jinja2'
    ],
    include_package_data=True,
    scripts=['src/ac.py'],
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
