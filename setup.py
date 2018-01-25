#!/usr/bin/env python3

from distutils.core import setup
from os.path import expanduser

with open('README.rst') as f:
    long_description = f.read()

setup(name = 'comp', version = '0.1.1a1',
      url = 'https://github.com/McSinyx/comp',
      description = ('Curses Online Media Player'),
      long_description=long_description,
      author = 'McSinyx', author_email = 'vn.mcsinyx@gmail.com',
      py_modules = ['mpv'], scripts=['comp'],
      data_files=[('/etc/comp', ['settings.ini'])],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: Console :: Curses',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Natural Language :: English',
          'Natural Language :: Vietnamese',  # planned
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.5',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Multimedia :: Video :: Display'
      ], license = 'AGPLv3')
