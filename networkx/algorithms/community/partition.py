# partition.py - functions for partitioning a graph
#
# Copyright 2011 Ben Edwards <bedwards@cs.unm.edu>.
# Copyright 2011 Aric Hagberg <hagberg@lanl.gov>.
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for partitioning a graph."""
from __future__ import division

from itertools import chain
from copy import deepcopy

try:
    import numpy as np
except ImportError:
    is_numpy_available = False
else:
    is_numpy_available = True

import networkx as nx
from networkx.utils import not_implemented_for
from .community_utils import is_partition
from .modularity import modularity

__all__ = ['spectral_modularity_partition', 'greedy_max_modularity_partition']

chaini = chain.from_iterable


def spectral_modularity_partition(G):
    r"""Returns a bipartition of the nodes based on the spectrum of the
    modularity matrix of the graph.

    This method calculates the eigenvector associated with the second
    largest eigenvalue of the modularity matrix, where the modularity
    matrix *B* is defined by

    ..math::

        B_{i j} = A_{i j} - \frac{k_i k_j}{2 m},

    where *A* is the adjacency matrix, `k_i` is the degree of node *i*,
    and *m* is the number of edges in the graph. Nodes whose
    corresponding values in the eigenvector are negative are placed in
    one block, nodes whose values are nonnegative are placed in another
    block.

    Parameters
    ----------
    G : NetworkX Graph

    Returns
    --------
    C : tuple
        Pair of sets of nodes of ``G``, partitioned according to second
        largest eigenvalue of the modularity matrix.

    Raises
    ------
    ImportError
        If ``NumPy`` is not available.

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> left, right = nx.spectral_modularity_partition(G)  # doctest: +SKIP
    >>> left, right = sorted(sorted(left), sorted(right))  # doctest: +SKIP
    >>> left  # doctest: +SKIP
    [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21]
    >>> right  # doctest: +SKIP
    [8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]

    Notes
    -----
    Defined for instances of the classes :class:`~networkx.Graph`,
    :class:`~networkx.DiGraph`, :class:`~networkx.MultiGraph`, and
    :class:`~networkx.MultiDiGraph`.

    References
    ----------
    .. [1] M. E. J. Newman *Networks: An Introduction*, pages 373--378
       Oxford University Press 2011.

    """
    if not is_numpy_available:
        raise ImportError('failed to import NumPy: http://www.numpy.org/')
    B = nx.modularity_matrix(G)
    eigenvalues, eigenvectors = np.linalg.eig(B)
    # Get the index of the largest eigenvalue.
    #
    # TODO Shouldn't this be -2?
    index = np.argsort(eigenvalues)[-1]
    v2 = zip(np.real(eigenvectors[:, index]), G)
    left, right = set(), set()
    for (u, n) in v2:
        if u < 0:
            left.add(n)
        else:
            right.add(n)
    return left, right


@not_implemented_for('multigraph')
def greedy_max_modularity_partition(G, C_init=None, max_iter=10):
    """Returns a bipartition of the nodes based using the greedy
    modularity maximization algorithm.

    The algorithm works by selecting a node to change communities which
    will maximize the modularity. The swap is made and the community
    structure with the highest modularity is kept.

    Parameters
    ----------
    G : NetworkX Graph

    C_init : tuple
        Pair of sets of nodes in ``G`` providing an initial bipartition
        for the algorithm. If not specified, a random balanced partition
        is used. If this pair is not a partition,
        :exc:`NetworkXException` is raised.

    max_iter : int
      Maximum number of times to attempt swaps to find an improvement
      before giving up.

    Returns
    -------
    C : tuple
        Pair of sets of nodes of ``G``, partitioned according to the
        greedy modularity maximization algorithm.

    Raises
    -------
    NetworkXError
      if C_init is not a valid partition of the
      graph into two communities or if G is a MultiGraph

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> left, right = nx.greedy_max_modularity_partition(G)
    >>> # Sort the communities so the nodes appear in increasing order.
    >>> left, right = sorted((sorted(left), sorted(right)))
    >>> sorted(left)
    [0, 1, 2]
    >>> sorted(right)
    [3, 4, 5]

    Notes
    -----
    This function is not implemented for multigraphs.

    References
    ----------
    .. [1] M. E. J. Newman "Networks: An Introduction", pages 373--375.
       Oxford University Press 2011.

    """
    if C_init is None:
        m1 = len(G) // 2
        m2 = len(G) - m1
        C = nx.random_partition(G, block_sizes=[m1, m2])
    else:
        if not is_partition(G, C_init):
            raise nx.NetworkXError("C_init is not a partition of G")
        if not len(C_init) == 2:
            raise nx.NetworkXError("C_init must be a bipartition")
        C = deepcopy(C_init)

    C_mod = modularity(G, C)
    Cmax = deepcopy(C)
    Cnext = deepcopy(C)

    Cmax_mod = C_mod
    Cnext_mod = C_mod

    itrs = 0

    m = G.number_of_edges()
    while Cmax_mod >= C_mod and itrs < max_iter:
        C = deepcopy(Cmax)
        C_mod = Cmax_mod
        Cnext = deepcopy(Cmax)
        Cnext_mod = Cmax_mod
        ns = set(G)
        while ns:
            max_swap = -1
            max_node = None
            max_node_comm = None
            left, right = Cnext
            leftd = sum(d for v, d in G.degree(left))
            rightd = sum(d for v, d in G.degree(right))
            for n in ns:
                if n in left:
                    in_comm, out_comm = left, right
                    in_deg, out_deg = leftd, rightd
                else:
                    in_comm, out_comm = right, left
                    in_deg, out_deg = rightd, leftd
                d_eii = -len(set(G.neighbors(n)) & in_comm) / m
                d_ejj = len(set(G.neighbors(n)) & out_comm) / m
                deg = G.degree(n)
                d_sum_ai = (deg / (2 * m ** 2)) * (in_deg - out_deg - deg)
                swap_change = d_eii + d_ejj + d_sum_ai
                if swap_change > max_swap:
                    max_swap = swap_change
                    max_node = n
                    max_node_comm = in_comm
                    non_max_node_comm = out_comm
            max_node_comm.remove(max_node)
            non_max_node_comm.add(max_node)
            Cnext_mod += max_swap
            ns.remove(max_node)
            if Cnext_mod > Cmax_mod:
                Cmax = deepcopy(Cnext)
                Cmax_mod = Cnext_mod
        itrs += 1
    return C

# # Recursive implementation.
#
# def recursive_dendrogram(G, partition_function, depth):
#     D = nx.Graph()
#
#     def _helper(communities, _depth):
#         if _depth <= 0:
#             return communities
#         newcomm = [partition_function(G.subgraph(c)) for c in C]
#         pairs = chaini((c, d for d in blocks) for c, blocks in zip(C,
#                                                                    newcomm))
#         D.add_edges_from((frozenset(c), frozenset(d)) for c, d in pairs)
#         newcomm = sum(newcomm, [])
#         return _helper(newcomm, _depth - 1)
#
#     return _helper([set(G)], depth)


def recursive_dendrogram(G, partition_function, depth):
    # Pre-condition: partition_function must return a nontrivial
    # partition as a list of sets.
    func = partition_function
    D = nx.Graph()
    communities = [set(G)]
    for i in range(depth):
        newcomm = [func(G.subgraph(c)) for c in communities]
        pairs = chaini(((c, d) for d in blocks)
                       for c, blocks in zip(communities, newcomm))
        D.add_edges_from((frozenset(c), frozenset(d)) for c, d in pairs)
        communities = sum(newcomm, [])
    return D


# # Recursive implementation.
#
# def recursive_partition(G, partition_function, depth):
#
#     def _helper(communities, _depth):
#         if _depth <= 0:
#             return communities
#         next_comm = sum((partition_function(G.subgraph(c)) for c in C), [])
#         return _helper(next_comm, _depth - 1)
#
#     return _helper([set(G)], depth)


def recursive_partition(G, partition_function, depth):
    # Pre-condition: partition_function must return a nontrivial
    # partition as a list of sets.
    func = partition_function
    communities = [set(G)]
    for i in range(depth):
        communities = sum((func(G.subgraph(c)) for c in communities), [])
    return communities
