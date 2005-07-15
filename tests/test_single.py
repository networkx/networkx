#!/usr/bin/env python
# alternative test by individual file
# e.g.
# python test4.py base_*.txt

import glob
import sys
import doctest
import unittest
import time
import os

if sys.version_info[:2] < (2, 4):
    print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
    sys.exit(-1)

nxbase=sys.path[0]+"/.."  # directory of networkx package (relative to this)
sys.path.insert(0,nxbase) # prepend to search path

try:
    import networkx
except:
    print "Can't import networkx module"
    print sys.path
    raise
    

# argv is list of modules to test
sys.argv.pop(0)

files=[]
for a in sys.argv:
    files.extend(glob.glob(a))


print ('Testing networkx %s with Python %s on %s at %s'
       % (networkx.__version__, sys.version.split()[0],
          time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S')))
sys.stdout.flush()

for fname in files:
    suite = unittest.TestSuite()
    s = doctest.DocFileSuite(fname,module_relative=False)
    suite.addTest(s)
    runner = unittest.TextTestRunner()
    runner.run(suite)
