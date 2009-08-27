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

if sys.version_info[:2] < (2, 4):
    print "NetworkX requires Python version 2.4 or later (%d.%d detected)." % \
          sys.version_info[:2]
    sys.exit(-1)

# Write the version information.
sys.path.insert(0, 'networkx')
import release
release.write_versionfile()
sys.path.pop(0)

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
          ]

docdirbase  = 'share/doc/networkx-%s' % release.version
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

    setup(
        name             = release.name,
        version          = release.version,
        maintainer       = release.maintainer,
        maintainer_email = release.maintainer_email,
        author           = release.authors['Hagberg'][0],
        author_email     = release.authors['Hagberg'][1],
        description      = release.description,
        keywords         = release.keywords,
        long_description = release.long_description,
        license          = release.license,
        platforms        = release.platforms,
        url              = release.url,      
        download_url     = release.download_url,
        classifiers      = release.classifiers,
        packages         = packages,
        data_files       = data,
        package_data     = package_data
      )

