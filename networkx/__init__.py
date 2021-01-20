"""
NetworkX
========

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://networkx.org for complete documentation.
"""

__version__ = "2.6rc1.dev0"

# These are import orderwise
from networkx.exception import *
import networkx.utils

import networkx.classes.filters
import networkx.classes
from networkx.classes import *

import networkx.convert
from networkx.convert import *

import networkx.convert_matrix
from networkx.convert_matrix import *


import networkx.relabel
from networkx.relabel import *

import networkx.generators
from networkx.generators import *

import networkx.readwrite
from networkx.readwrite import *

# Need to test with SciPy, when available
import networkx.algorithms
from networkx.algorithms import *

import networkx.linalg
from networkx.linalg import *

from networkx.testing.test import run as test

import networkx.drawing
from networkx.drawing import *
