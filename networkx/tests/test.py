#!/usr/bin/env python

import glob
import os
import sys
import doctest
import unittest


def all():
    import networkx
    testdirs=['.','algorithms','classes','drawing','generators',
              'linalg','readwrite','algorithms/isomorphism',
              'algorithms/traversal']
    try:
        from pkg_resources import resource_filename, resource_listdirfoo
        tests=[]
        for d in testdirs:
            
            tests.extend([resource_filename(networkx.__name__, 
                                            "%s/tests/%s"%(d,t))
                          for t in resource_listdir("networkx","%s/tests"%d)
                          if t.endswith("txt")])
    except:
        import networkx
        base=os.path.dirname(networkx.__file__)
        tests=[]
        for d in testdirs:
            tests+=glob.glob(os.path.join(base,d,"tests","*.txt"))
    skiplist=[]        

    try:
        import numpy
    except ImportError:
        print "numpy not found: skipping tests"
        skiplist.extend(['spectrum.txt','threshold.txt'])
    try:
        import yaml
    except ImportError:
        print "yaml not found: skipping tests"
        skiplist.extend(['nx_yaml.txt'])
    try:
        import pyparsing
    except ImportError:
        print "pyparsing not found: skipping tests"
        skiplist.extend(['gml.txt'])
    try:
        import pydot
    except ImportError:
        print "pydot not found: skipping tests"
        skiplist.extend(['nx_pydot.txt'])
    try:
        import pygraphviz
    except ImportError:
        print "pygraphviz not found: skipping tests"
        skiplist.extend(['nx_agraph.txt'])
    try:
        import matplotlib
        import pylab
    except ImportError:
        print "matplotlib not found: skipping tests"
        skiplist.extend(['nx_pylab.txt'])


    tests=[t for t in tests if os.path.basename(t) not in skiplist]

    suite = unittest.TestSuite()
    for t in tests:
        s = doctest.DocFileSuite(t,module_relative=False)
        suite.addTest(s)
    return suite

def run():
    runner = unittest.TextTestRunner()
    runner.run(all())
    

if __name__ == "__main__":
    run()
