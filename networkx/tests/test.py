#!/usr/bin/env python

import glob
import os
import sys
import doctest
import unittest

def all():
    try:
        # import ez_setup # force use of setuptools
        # ez_setup.use_setuptools()
        from pkg_resources import resource_filename, resource_listdir
        tests=[resource_filename(__name__, t)
              for t in resource_listdir("networkx",'tests') if t.endswith("txt")]
        tests+=[resource_filename(__name__, 'generators/'+t)
              for t in resource_listdir("networkx",'tests/generators') if t.endswith("txt")]
    except:
        tests=glob.glob("*.txt") # this will only work from test directory   
        tests+=glob.glob("generators/*.txt")
        #tests+=glob.glob("drawing/*.txt")  

    # skip some tests if we don't have numpy or Numeric        
    try:
        import numpy
    except ImportError:
        try:
            import Numeric
        except ImportError:
            print "Neither numpy or Numeric found."
            print "Skipping tests of spectrum.py and threshold.py"
            tests.remove('spectrum.txt')
            tests.remove('threshold.txt')
#            tests=[t for t in tests if 'spectrum.txt' not in t \
#                    if 'threshold.txt' not in t]


    suite = unittest.TestSuite()
    for t in tests:
        s = doctest.DocFileSuite(t,module_relative=False)
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
