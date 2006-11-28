#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for networkx

"""

from glob import glob
import os
import sys
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

from distutils.core import setup

if sys.argv[-1] == 'setup.py':
    print "To install, run 'python setup.py install'"
    print

if sys.version_info[:2] < (2, 3):
    print "NX requires Python version 2.3 or later (%d.%d detected)." % \
          sys.version_info[:2]
    sys.exit(-1)

execfile(os.path.join('networkx','release.py'))

packages=["networkx",
          "networkx.generators",
          "networkx.drawing",
          "networkx.tests",
          "networkx.tests.generators",
          "networkx.tests.drawing",
          ]

docdirbase  = 'share/doc/networkx-%s' % version
data = [(docdirbase, glob("doc/*.txt")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*.py")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*.dat")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*.edges")),
        (os.path.join(docdirbase, 'data'),glob("doc/data/*ls")),
        ]

setup(name             = name,
      version          = version,
      author           = authors['Hagberg'][0],
      author_email     = authors['Hagberg'][1],
      description      = description,
      keywords         = keywords,
      long_description = long_description,
      license          = license,
      platforms        = platforms,
      url              = url,      
      download_url     = download_url,
      packages         = packages,
      data_files      =  data,
      package_data     = {'': ['*.txt'],}, 
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        ]
      )

