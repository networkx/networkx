#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for networkx.

"""
# Lots of good ideas borrowed from the IPython setup script
# http://ipython.scipy.org/
# Thanks to Fernando Perez

from glob import glob
import os
import string
import sys
import time
isfile = os.path.isfile

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

from distutils.core import setup
import setupext

if sys.argv[-1] == 'setup.py':
    print "To install, run 'python setup.py install'"
    print

if sys.version_info[:2] < (2, 3):
    print "NX requires Python version 2.3 or later (%d.%d detected)." % \
          sys.version_info[:2]
    sys.exit(-1)

execfile(os.path.join('networkx','release.py'))


# A little utility we'll need below, since glob() does NOT allow you to do
# exclusion on multiple endings!
def file_doesnt_endwith(test,endings):
    """Return true if test is a file and its name does NOT end with any
    of the strings listed in endings."""
    if not isfile(test):
        return False
    for e in endings:
        if test.endswith(e):
            return False
    return True


docdirbase  = 'share/doc/networkx-%s' % version
docfiles = filter(isfile, glob('doc/*'))
examples = filter(isfile, glob('examples/*.py')) + \
           filter(isfile, glob('examples/*.dat')) + \
           filter(isfile, glob('examples/*.edges'))
html     = filter(isfile, glob('doc/html/*'))
ref      = filter(isfile, glob('doc/html/Reference/*'))
pdf      = filter(isfile, glob('doc/pdf/*.pdf')) 
tests    = filter(isfile, glob('networkx/tests/*')) 

data = [('data', docdirbase, docfiles),
        ('data', os.path.join(docdirbase, 'examples'), examples),
        ('data', os.path.join(docdirbase, 'html'), html),
        ('data', os.path.join(docdirbase, 'html/Reference'), ref),
        ('data', os.path.join(docdirbase, 'pdf'), pdf),
        ('data', os.path.join(docdirbase, 'tests'), tests)
        ]

packages=["networkx","networkx.generators","networkx.drawing"]

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
      packages         = packages,
      cmdclass         = {'install_data': setupext.install_data_ext},
      data_files       = data
      )


try:
    import Numeric 
except:
    print "Import Error: not able to import Numeric."
    print "Some functionality may be unavailable."
    print "See http://numpy.sf.net/ for this package."
    print
    pass

try:
    import matplotlib
except:
    print "Import Error: not able to import matplotlib."
    print "Some functionality may be unavailable."
    print "See http://matplotlib.sourceforge.net/ for this package."
    print
    pass

try:
    import pydot
except:
    print "Import Error: not able to import pydot."
    print "Some functionality may be unavailable."
    print "See http://dkbza.org/pydot.html for this package."
    print
    pass
