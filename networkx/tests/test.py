#!/usr/bin/env python

import glob
import os
import sys
import doctest
import unittest


# FIXME: exclude optional drawing packages if not installed
def all():
    from pkg_resources import resource_filename
    suite = unittest.TestSuite()
    testdir=sys.path[1]+os.sep+"networkx"+os.sep+"tests"
    for testfile in glob.glob1(testdir,"*.txt"):
        doctst = resource_filename(__name__, testfile)
        s = doctest.DocFileSuite(doctst,module_relative=False)
        suite.addTest(s)
    return suite

if __name__ == "__main__":
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)

    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    try:
        import networkx
    except:
        print "Can't import networkx module, not in path"
        print sys.path
        raise
    
    runner = unittest.TextTestRunner()
    runner.run(all())
