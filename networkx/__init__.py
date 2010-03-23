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
#    All rights reserved.
#    BSD license.
#
# Add platform dependent shared library path to sys.path
#
import sys
if sys.version_info[:2] < (2, 4):
    raise ImportError("Python version 2.4 or later is required for NetworkX (%d.%d detected)." %  sys.version_info[:2])

del sys

# Release data
import release 

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

from exception import  *

from algorithms import *
from classes import *
from convert import *
from drawing import *
from generators import *
from linalg import *
from readwrite import *

import utils
from tests.test import run as test
import algorithms
import classes
import convert
import drawing
import generators
import linalg
import readwrite

