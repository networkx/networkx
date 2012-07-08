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
    >>> G.add_node(42)
    >>> print(sorted(G.nodes()))
    [1, 2, 42]
    >>> print(sorted(G.edges()))
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

from __future__ import absolute_import

import sys
if sys.version_info[:2] < (2, 6):
    m = "Python version 2.6 or later is required for NetworkX (%d.%d detected)."
    raise ImportError(m % sys.version_info[:2])
del sys

# Release data
from networkx import release

__author__   = '%s <%s>\n%s <%s>\n%s <%s>' % \
              ( release.authors['Hagberg'] + release.authors['Schult'] + \
                release.authors['Swart'] )
__license__  = release.license

__date__ = release.date
__version__ = release.version

#These are import orderwise
from networkx.exception import  *
import networkx.external
import networkx.utils
# these packages work with Python >= 2.6

import networkx.classes
from networkx.classes import *


import networkx.convert
from networkx.convert import *

import networkx.relabel
from networkx.relabel import *

import networkx.generators
from networkx.generators import *

import networkx.readwrite
from networkx.readwrite import *

#Need to test with SciPy, when available
import networkx.algorithms
from networkx.algorithms import *
import networkx.linalg

from networkx.linalg import *
from networkx.tests.test import run as test

import networkx.drawing
from networkx.drawing import *

