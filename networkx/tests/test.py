#!/usr/bin/env python

import glob
import os
import sys
import doctest
import unittest

def all():
    try:
        from pkg_resources import resource_filename, resource_listdir
        tests=[resource_filename(__name__, t)
              for t in resource_listdir("networkx",'tests') if t.endswith("txt")]
        tests+=[resource_filename(__name__, 'generators/'+t)
              for t in resource_listdir("networkx",'tests/generators') if t.endswith("txt")]
        tests+=[resource_filename(__name__, 'readwrite/'+t)
              for t in resource_listdir("networkx",'tests/readwrite') if t.endswith("txt")]
    except:
        import networkx
        base=os.path.dirname(networkx.__file__)+"/tests/"
        tests=glob.glob(base+"*.txt") 
        tests+=glob.glob(base+"generators/*.txt")
        tests+=glob.glob(base+"readwrite/*.txt")
        #tests+=glob.glob("drawing/*.txt")  

    # tests depending on numpy
    try:
        import numpy
    except ImportError:
        print "numpy not found: skipping tests of spectrum.py, threshold.py, convert.py (numpy)"
        tests=[t for t in tests \
               if 'spectrum.txt' not in t \
               if 'threshold.txt' not in t\
               if 'convert_numpy.txt' not in t\
               ]

    # tests depending on scipy        
    try:
        import scipy
    except ImportError:
        print "scipy not found: skipping tests of convert.py (scipy)"
        tests=[t for t in tests \
               if 'convert_scipy.txt' not in t\
               ]
    # tests depending on yaml        
    try:
        import yaml
    except ImportError:
        print "yaml not found: skipping tests of nx_yaml.py (yaml)"
        tests=[t for t in tests \
               if 'nx_yaml.txt' not in t\
               ]
    # tests depending on pyparsing
    try:
        import pyparsing
    except ImportError:
        print "pyparsing not found: skipping tests of gml.py"
        tests=[t for t in tests \
               if 'gml.txt' not in t\
               ]





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
