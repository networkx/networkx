#!/usr/bin/env python

import glob
import os
import sys
import doctest
import unittest
import networkx


def all():
    from pkg_resources import resource_filename
    suite = unittest.TestSuite()
    testdir=networkx.__path__[0]+os.sep+"tests"
    for testfile in glob.glob1(testdir,"*.txt"):
        doctst = resource_filename(__name__, testfile)
        s = doctest.DocFileSuite(doctst,module_relative=False)
        suite.addTest(s)
    return suite

def run():
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    runner = unittest.TextTestRunner()
    runner.run(all())
    

if __name__ == "__main__":
    try:
        import networkx
    except:
        print "Can't import networkx module, not in path"
        print sys.path
        raise
    
    run()
