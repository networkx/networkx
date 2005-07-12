#!/usr/bin/env python
import unittest
import doctest
import sys
import time
import os
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)"""
__date__ = "$Date: 2005-03-30 16:56:28 -0700 (Wed, 30 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 911 $"

if sys.version_info[:2] < (2, 4):
    print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
    sys.exit(-1)

nxbase=sys.path[0]+"/../.."  # directory of NX package (relative to this)
sys.path.insert(0,nxbase)    # prepend to search path

try:
    import NX
except:
    "Can't import NX module"
    raise
    

# list of modules to test

mlist= ['NX.base',
        'NX.centrality',
        'NX.cliques',
        'NX.cluster',
        'NX.cores',
        'NX.drawing.layout',
        'NX.drawing.nx_pylab',
        'NX.drawing.nx_pydot',
        'NX.generators.atlas',
        'NX.generators.classic',
        'NX.generators.degree_seq',
        'NX.generators.geometric',
        'NX.generators.random_graphs',
        'NX.generators.small',
        'NX.hybrid',
        'NX.io',
        'NX.isomorph',
        'NX.operators',
        'NX.paths',
        'NX.queues',
        'NX.search',
        'NX.search_class',
        'NX.spectrum',
        'NX.utils',
        'NX.xbase'
        ]

print ('Testing NX %s with Python %s on %s at %s'
       % (NX.__version__, sys.version.split()[0],
          time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S')))
sys.stdout.flush()



suite = unittest.TestSuite()
runner = unittest.TextTestRunner()
for mod in mlist:
    sys.stderr.write("%s\n"%mod)
    try: 
        m=__import__(mod,"","","*")
    except:
        sys.stderr.write("skipping %s\n"%mod)
        continue
    suite.addTest(m._test_suite())
runner.run(suite)


