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
          "networkx.util",
          "networkx.tests",
          ]

docdirbase  = 'share/doc/networkx-%s' % version
# add basic documentation 
data = [(docdirbase, glob("*.txt"))]
# add examples
for d in ['advanced',
          'algorithms',
          'basic',
          'drawing',
          'graph',
          'multigraph',
          'pygraphviz',
          'readwrite',
          'ubigraph']:
    dd=os.path.join(docdirbase,'examples',d)
    pp=os.path.join('examples',d)
    data.append((dd,glob(os.path.join(pp,"*.py"))))
    data.append((dd,glob(os.path.join(pp,"*.bz2"))))
    data.append((dd,glob(os.path.join(pp,"*.gz"))))
    data.append((dd,glob(os.path.join(pp,"*.mbox"))))
    data.append((dd,glob(os.path.join(pp,"*.edgelist"))))

# add the tests
package_data     = {'': ['tests/*.py'],
                    '': ['tests/*.txt'],
                    }

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

