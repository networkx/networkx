# __init__.py - package containing heuristics for optimization problems
#
# Copyright 2016-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Approximations of graph properties and Heuristic functions for optimization
problems.

    .. warning:: The approximation submodule is not imported in the top-level
        ``networkx``.

    These functions can be imported with
    ``from networkx.algorithms import approximation``.

"""

from .clustering_coefficient import *
from .clique import *
from .connectivity import *
from .dominating_set import *
from .kcomponents import *
from .independent_set import *
from .matching import *
from .ramsey import *
from .steinertree import *
from .vertex_cover import *
from .treewidth import *
from .christofides import *