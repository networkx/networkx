# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Efraim Rodrigues (efraimnaassom@gmail.com)
r"""Generators for cographs

A cograph is a graph containing no path on four vertices.
Cographs or $P_4$-free graphs can be obtained from a single vertex
by disjoint union and complementation operations.

References
----------
.. [1] D.G. Corneil, H. Lerchs, L.Stewart Burlingham,
       "Complement reducible graphs",
    Discrete Applied Mathematics, Volume 3, Issue 3, 1981, Pages 163-174,
    ISSN 0166-218X.
"""
import networkx as nx
from networkx.utils import py_random_state

__all__ = ['random_cograph']


@py_random_state(1)
def random_cograph(n, seed=None):
    """Returns a random cograph with $2 ^ n$ nodes.

    Parameters
    ----------
    n : int
            The order of the cograph.
    seed : integer, random_state, or None (default)
            Indicator of random number generation state.
            See :ref:`Randomness<randomness>`.

    See Also
    --------
    union

    Notes
    -----
    This generator starts off from a single vertex and performes disjoint
    union and full join operations on itself.
    The decision on which operation will take place is random.
    """
    R = nx.empty_graph(1)

    for i in range(n):
        r = seed.randint(0, 1)

        def label(x):
            return x + len(R)

        if r:
            R = nx.full_join(R, nx.relabel_nodes(R.copy(), label))
        else:
            R = nx.disjoint_union(R,
                                  nx.relabel_nodes(R.copy(), label)
                                  )

    return R
