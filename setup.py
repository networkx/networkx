#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for networkx

"""

from glob import glob
import os
import sys
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'setup.py':
    print "To install, run 'python setup.py install'"
    print

if sys.version_info[:2] < (2, 4):
    print "NetworkX requires Python version 2.4 or later (%d.%d detected)." % \
          sys.version_info[:2]
    sys.exit(-1)

execfile(os.path.join('networkx','release.py'))

packages=["networkx",
          "networkx.algorithms",
          "networkx.algorithms.traversal",
          "networkx.algorithms.isomorphism",
          "networkx.classes",
          "networkx.generators",
          "networkx.drawing",
          "networkx.linalg",
          "networkx.readwrite",
          "networkx.tests",
          "networkx.algorithms.tests",
          "networkx.algorithms.traversal.tests",
          "networkx.algorithms.isomorphism.tests",
          "networkx.classes.tests",
          "networkx.generators.tests",
          "networkx.drawing.tests",
          "networkx.linalg.tests",
          "networkx.readwrite.tests",
          ]

docdirbase  = 'share/doc/networkx-%s' % version
data = [(docdirbase, glob("doc/*.rst")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*/*.py")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*/*.dat")),
        (os.path.join(docdirbase, 'examples'),glob("doc/examples/*/*.edges")),
        ]

package_data     = {'': ['*.txt'],} 


if __name__ == "__main__":

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
      data_files       = data,
      package_data     = package_data, 
      classifiers      = classifiers,
      )

