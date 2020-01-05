#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
from os.path import abspath, join, dirname

name = 'Mikko Korpela'
# I might be just a little bit too much afraid of those bots..
address = name.lower().replace(' ', '.')+chr(64)+'gmail.com'

desc = 'Train and use expectation detector in Robot Framework tests.'

CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'README.rst')) as f:
    LONG_DESCRIPTION = f.read()

setup(name='robotframework-expects',
      version='0.1.1',
      description=desc,
      long_description=LONG_DESCRIPTION,
      author=name,
      author_email=address,
      url='https://github.com/mkorpela/robotframework-expects',
      packages=find_packages(),
      license='Apache License, Version 2.0',
      keywords=['testing'],
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
          ]
      )
