"""
NetworkX
========

   NetworkX (NX) is a Python package for the creation, manipulation, and
   study of the structure, dynamics, and functions of complex networks.  

   https://networkx.lanl.gov/

Using 
-----

   Just write in Python

   >>> import networkx as nx
   >>> G=nx.Graph()
   >>> G.add_edge(1,2)
   >>> G.add_node("spam")
   >>> print G.nodes()
   [1, 2, 'spam']
   >>> print G.edges()
   [(1, 2)]
"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#
# Add platform dependent shared library path to sys.path
#
import sys
if sys.version_info[:2] < (2, 3):
    print "Python version 2.3 or later is required for NetworkX (%d.%d detected)." %  sys.version_info[:2]
    sys.exit(-1)
del sys
# Release data
import release 
__version__  = release.version
__date__     = release.date
__author__   = '%s <%s>\n%s <%s>\n%s <%s>' % \
              ( release.authors['Hagberg'] + release.authors['Schult'] + \
                release.authors['Swart'] )
__license__  = release.license
__revision__ = release.revision

from exception import  NetworkXException, NetworkXError

from algorithms import *
from classes import *
from convert import *
from drawing import *
from generators import *
from linalg import *
from operators import *
from readwrite import *
from ubigraph import *

import utils
from tests.test import run as test
import algorithms
import classes
import convert
import drawing
import generators
import linalg
import operators
import readwrite

