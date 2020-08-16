"""
NetworkX
========

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://networkx.github.io for complete documentation.
"""

import sys

if sys.version_info[:2] < (3, 6):
    m = "Python 3.6 or later is required for NetworkX (%d.%d detected)."
    raise ImportError(m % sys.version_info[:2])
del sys

# Release data
from networkx import release


__author__ = (
    f"{release.authors['Hagberg'][0]} <{release.authors['Hagberg'][1]}>\n"
    f"{release.authors['Schult'][0]} <{release.authors['Schult'][1]}>\n"
    f"{release.authors['Swart'][0]} <{release.authors['Swart'][1]}>"
)

__date__ = release.date
__version__ = release.version

__bibtex__ = """@inproceedings{hagberg-2008-exploring,
author = {Aric A. Hagberg and Daniel A. Schult and Pieter J. Swart},
title = {Exploring network structure, dynamics, and function using {NetworkX}},
year = {2008},
month = Aug,
urlpdf = {http://math.lanl.gov/~hagberg/Papers/hagberg-2008-exploring.pdf},
booktitle = {Proceedings of the 7th Python in Science Conference (SciPy2008)},
editors = {G\"{a}el Varoquaux, Travis Vaught, and Jarrod Millman},
address = {Pasadena, CA USA},
pages = {11--15}
}"""

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
