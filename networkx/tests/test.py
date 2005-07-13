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

nxbase=sys.path[0]+"/../.."  # directory of networkx package (relative to this)
sys.path.insert(0,nxbase)    # prepend to search path

try:
    import networkx
except:
    "Can't import networkx module"
    raise
    

# list of modules to test

mlist= ['networkx.base',
        'networkx.centrality',
        'networkx.cliques',
        'networkx.cluster',
        'networkx.cores',
        'networkx.drawing.layout',
        'networkx.drawing.nx_pylab',
        'networkx.drawing.nx_pydot',
        'networkx.generators.atlas',
        'networkx.generators.classic',
        'networkx.generators.degree_seq',
        'networkx.generators.geometric',
        'networkx.generators.random_graphs',
        'networkx.generators.small',
        'networkx.hybrid',
        'networkx.io',
        'networkx.isomorph',
        'networkx.operators',
        'networkx.paths',
        'networkx.queues',
        'networkx.search',
        'networkx.search_class',
        'networkx.spectrum',
        'networkx.utils',
        'networkx.xbase'
        ]

print ('Testing networkx %s with Python %s on %s at %s'
       % (networkx.__version__, sys.version.split()[0],
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


