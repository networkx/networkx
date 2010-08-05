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
   >>> print(G.nodes())
   [1, 2, 'spam']
   >>> print(G.edges())
   [(1, 2)]
"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Add platform dependent shared library path to sys.path
#
import sys
if sys.version_info[:2] < (2, 6):
    raise ImportError("Python version 2.6 or later is required for NetworkX (%d.%d detected)." %  sys.version_info[:2])

# Release data
from networkx import release

if release.revision is None:
    # we probably not running in an svn directory   
    try:
        # use release data stored at installatation time.
        import version
        __version__ = version.__version__
        __revision__ = version.__revision__
        __date__ = version.__date__
    except ImportError:
        # version.py was not created or no longer exists
        __version__ = release.version
        __revision__ = release.revision
        __date__ = release.date
else:
    # use dynamic values, even if version.py exists
    __version__ = release.version
    __revision__ = release.revision
    __date__ = release.date

__author__   = '%s <%s>\n%s <%s>\n%s <%s>' % \
              ( release.authors['Hagberg'] + release.authors['Schult'] + \
                release.authors['Swart'] )
__license__  = release.license

# these packages work with Python >= 2.6 
from networkx.exception import  *
import networkx.classes
from networkx.classes import *
import networkx.convert
from networkx.convert import *
import networkx.generators
from networkx.generators import *
from networkx.readwrite import *
import networkx.readwrite
#Need to test with SciPy, when available
import networkx.algorithms
from networkx.algorithms import *
import networkx.linalg
from networkx.linalg import *
from networkx.tests.test import run as test
import networkx.utils

import networkx.drawing
from networkx.drawing import *

del sys

