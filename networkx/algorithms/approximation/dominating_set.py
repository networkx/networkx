# -*- coding: utf-8 -*-
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
"""Functions for finding node and edge dominating sets.

A *`dominating set`_[1] for an undirected graph *G* with vertex set *V*
and edge set *E* is a subset *D* of *V* such that every vertex not in
*D* is adjacent to at least one member of *D*. An *`edge dominating
set`_[2] is a subset *F* of *E* such that every edge not in *F* is
incident to an endpoint of at least one edge in *F*.

.. [1] dominating set: https://en.wikipedia.org/wiki/Dominating_set
.. [2] edge dominating set: https://en.wikipedia.org/wiki/Edge_dominating_set

"""
from __future__ import division

from collections import Counter
from itertools import chain

from ..matching import maximal_matching
from ...utils import not_implemented_for

__all__ = ["min_weighted_dominating_set",
           "min_edge_dominating_set"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""

INF = float('inf')


# TODO Why doesn't this algorithm work for directed graphs?
@not_implemented_for('directed')
def min_weighted_dominating_set(G, weight=None, _postprocessing=False):
    r"""Returns a dominating set that approximates the minimum weight node
    dominating set.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph.

    weight : string
        The node attribute storing the weight of an edge. If provided,
        the node attribute with this key must be a number for each
        node. If not provided, each node is assumed to have weight one.

    Other parameters
    ----------------
    _postprocessing : bool
        If ``True``, an additional postprocessing step is performed that
        reduces the size of the returned dominating set but increases
        the asymptotic time complexity of this function.

    Returns
    -------
    min_weight_dominating_set : set
        A set of nodes, the sum of whose weights is no more than `(\log
        w(V)) w(V^*)`, where `w(V)` denotes the sum of the weights of
        each node in the graph and `w(V^*)` denotes the sum of the
        weights of each node in the minimum weight dominating set.

    Notes
    -----
    This algorithm computes an approximate minimum weighted dominating
    set for the graph ``G``. The returned solution has weight `(\log
    w(V)) w(V^*)`, where `w(V)` denotes the sum of the weights of each
    node in the graph and `w(V^*)` denotes the sum of the weights of
    each node in the minimum weight dominating set for the graph.

    This implementation of the algorithm runs in `O(n^2)` time (ignoring
    logarithmic factors), where `n` is the number of nodes in the graph.

    If the ``_postprocessing`` keyword argument is ``True``, then an
    additional postprocessing heuristic from [2]_ is run. This
    additional postprocessing increases the running time of this
    function to `O(n(n + m))`.

    References
    ----------
    .. [1] Vazirani, Vijay V.
           *Approximation Algorithms*.
           Springer Science & Business Media, 2001.
    .. [2] Grossman, Tal, and Avishai Wool.
           "Computational Experience with Approximation Algorithms
           for the Set Covering Problem."
           European Journal of Operational Research 101.1 (1997): 81-92.
           <http://dx.doi.org/10.1016/S0377-2217(96)00161-0>.

    """
    # The unique dominating set for the null graph is the empty set.
    if len(G) == 0:
        return set()

    # This is the dominating set that will eventually be returned.
    dom_set = set()
    # This is a set of all nodes not already covered by the dominating
    # set.
    nodes = set(G)

    def _cost(node_and_neighborhood):
        """Returns the cost-effectiveness of greedily choosing the given
        node.

        `node_and_neighborhood` is a two-tuple comprising a node and its
        closed neighborhood.

        """
        v, neighborhood = node_and_neighborhood
        covered_nodes = neighborhood & nodes
        if covered_nodes:
            return G.node[v].get(weight, 1) / len(covered_nodes)
        # If this neighborhood doesn't cover any of the remaining
        # undominated nodes, the cost of the node is very high.
        return INF

    # This is a dictionary mapping each node to the closed neighborhood
    # of that node.
    neighborhoods = {v: {v} | set(G[v]) for v in G}

    # Continue until all nodes are adjacent to some node in the
    # dominating set.
    while nodes:
        # Find the most cost-effective node to add, along with its
        # closed neighborhood.
        dom_node, min_set = min(neighborhoods.items(), key=_cost)
        # Add the node to the dominating set and reduce the remaining
        # set of nodes to cover.
        dom_set.add(dom_node)
        del neighborhoods[dom_node]
        nodes -= min_set

    if _postprocessing:
        # Determine the number of times each node in the graph has been
        # covered by some node in the approximate dominating set.
        depth = Counter(chain.from_iterable({u} | set(G[u]) for u in dom_set))

        # Compute the minimum depth of the nodes in each particular
        # closed neighborhood.
        def _redundancy(u):
            return min(depth[v] for v in {u} | set(G[u])) - 1
        redundancy = {u: _redundancy(u) for u in dom_set}
        # Find the node with the highest redundancy. Break ties in favor
        # of more heavily weighted nodes.
        sortkey = lambda pair: (pair[1], G.node[pair[0]].get(weight, 1))
        redun_node, max_redun = max(redundancy.items(), key=sortkey)
        # While there remains a redundant node, remove it from the
        # dominating set and repeat.
        while max_redun > 0:
            dom_set -= {redun_node}
            del redundancy[redun_node]
            depth.subtract({redun_node} | set(G[redun_node]))
            redundancy = {u: _redundancy(u) for u in dom_set}
            redun_node, max_redun = max(redundancy.items(), key=sortkey)

    return dom_set


def min_edge_dominating_set(G):
    r"""Return minimum cardinality edge dominating set.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    Returns
    -------
    min_edge_dominating_set : set
      Returns a set of dominating edges whose size is no more than 2 * OPT.

    Notes
    -----
    The algorithm computes an approximate solution to the edge dominating set
    problem. The result is no more than 2 * OPT in terms of size of the set.
    Runtime of the algorithm is `O(|E|)`.
    """
    if not G:
        raise ValueError("Expected non-empty NetworkX graph!")
    return maximal_matching(G)
