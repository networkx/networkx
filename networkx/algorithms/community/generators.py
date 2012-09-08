# generators.py - functions for generating communities in a graph
#
# Copyright 2011 Ben Edwards <bedwards@cs.unm.edu>.
# Copyright 2011 Aric Hagberg <hagberg@lanl.gov>.
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for generating communities in a graph."""
import random

import networkx as nx


__all__ = ['random_partition']


def random_partition(G, block_sizes):
    """Partition the nodes of a graph into blocks of the specified
    sizes.

    Parameters
    ----------
    G : NetworkX graph

    block_sizes : iterable
        Iterable of integers representing the sizes of the blocks in the
        generated partition.

    Returns
    -------
    C : list
        List of sets of nodes of ``G`` representing a partition of the
        graph. The block ``C[i]`` will have size ``block_sizes[i]``, for
        each index ``i``.

    Raises
    ------
    NetworkXError
        If the sum of the block sizes does not equal the number of nodes
        in the graph.

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> nx.random_partition(G, block_sizes=[3, 7])  # doctest: +SKIP
    [{2, 5, 6}, {0, 1, 3, 4, 7, 8, 9}]

    """
    if sum(block_sizes) != len(G):
        raise nx.NetworkXError('block sizes must sum to len(G)')
    C = [set() for _ in range(len(block_sizes))]
    ns = list(G)
    for block, size in zip(C, block_sizes):
        for _ in range(size):
            n = ns.pop(random.randrange(0, len(ns)))
            block.add(n)
    return C
