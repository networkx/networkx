#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
"""
Find the k-cores of a graph.

The k-core is found by recursively pruning nodes with degrees less than k.

See the following reference for details:

An O(m) Algorithm for Cores Decomposition of Networks
Vladimir Batagelj and Matjaz Zaversnik, 2003.
http://arxiv.org/abs/cs.DS/0310049

"""

__author__ = "\n".join(['Dan Schult (dschult@colgate.edu)',
                        'Jason Grout (jason-sage@creativetrax.com)',
                        'Aric Hagberg (hagberg@lanl.gov)'])

__all__ = ['core_number','k_core','k_shell','k_crust','k_corona','find_cores']

import networkx as nx
from networkx import all_neighbors
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for

@not_implemented_for('multigraph')
def core_number(G):
    """Return the core number for each vertex.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    The core number of a node is the largest value k of a k-core containing
    that node.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph

    Returns
    -------
    core_number : dictionary
       A dictionary keyed by node to the core number.

    Raises
    ------
    NetworkXError
        The k-core is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik, 2003.
       http://arxiv.org/abs/cs.DS/0310049
    """
    if G.number_of_selfloops() > 0:
        raise NetworkXError(
                'Input graph has self loops; the core number is not defined.'
                ' Consider using G.remove_edges_from(G.selfloop_edges()).')
    degrees = dict(G.degree())
    # Sort nodes by degree.
    nodes = sorted(degrees, key=degrees.get)
    bin_boundaries = [0]
    curr_degree = 0
    for i, v in enumerate(nodes):
        if degrees[v] > curr_degree:
            bin_boundaries.extend([i] * (degrees[v]-curr_degree))
            curr_degree = degrees[v]
    node_pos = {v: pos for pos, v in enumerate(nodes)}
    # The initial guess for the core number of a node is its degree.
    core = degrees
    nbrs = {v: set(all_neighbors(G, v)) for v in G}
    for v in nodes:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos = node_pos[u]
                bin_start = bin_boundaries[core[u]]
                node_pos[u] = bin_start
                node_pos[nodes[bin_start]] = pos
                nodes[bin_start], nodes[pos] = nodes[pos], nodes[bin_start]
                bin_boundaries[core[u]] += 1
                core[u] -= 1
    return core


find_cores = core_number


def _core_helper(G, func, k=None, core=None):
    """Returns the subgraph induced by all nodes for which ``func``
    returns ``True``.

    ``G`` is a NetworkX graph.

    ``func`` is a function that takes three inputs: a node of ``G``, the
    maximum core value, and the core number of the graph. The function
    must return a Boolean value.

    ``k`` is the order of the core. If not specified, the maximum over
    all core values will be returned.

    ``core`` is a dictionary mapping node to core numbers for that
    node. If you have already computed it, you should provide it
    here. If not specified, the core numbers will be computed from the
    graph.

    """
    if core is None:
        core = core_number(G)
    if k is None:
        k = max(core.values())
    nodes = [v for v in core if func(v, k, core)]
    return G.subgraph(nodes).copy()


def k_core(G,k=None,core_number=None):
    """Return the k-core of G.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    k : int, optional
      The order of the core.  If not specified return the main core.
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-core subgraph

    Raises
    ------
    NetworkXError
      The k-core is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    The main core is the core with the largest degree.

    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik,  2003.
       http://arxiv.org/abs/cs.DS/0310049
    """
    func = lambda v, k, core_number: core_number[v] >= k
    return _core_helper(G, func, k, core_number)


def k_shell(G,k=None,core_number=None):
    """Return the k-shell of G.

    The k-shell is the subgraph of nodes in the k-core but not in the (k+1)-core.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph.
    k : int, optional
      The order of the shell.  If not specified return the main shell.
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.


    Returns
    -------
    G : NetworkX graph
       The k-shell subgraph

    Raises
    ------
    NetworkXError
        The k-shell is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    This is similar to k_corona but in that case only neighbors in the
    k-core are considered.

    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number
    k_corona


    References
    ----------
    .. [1] A model of Internet topology using k-shell decomposition
       Shai Carmi, Shlomo Havlin, Scott Kirkpatrick, Yuval Shavitt,
       and Eran Shir, PNAS  July 3, 2007   vol. 104  no. 27  11150-11154
       http://www.pnas.org/content/104/27/11150.full
    """
    func = lambda v, k, core_number: core_number[v] == k
    return _core_helper(G, func, k, core_number)


def k_crust(G,k=None,core_number=None):
    """Return the k-crust of G.

    The k-crust is the graph G with the k-core removed.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph.
    k : int, optional
      The order of the shell.  If not specified return the main crust.
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
       The k-crust subgraph

    Raises
    ------
    NetworkXError
        The k-crust is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    This definition of k-crust is different than the definition in [1]_.
    The k-crust in [1]_ is equivalent to the k+1 crust of this algorithm.

    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number

    References
    ----------
    .. [1] A model of Internet topology using k-shell decomposition
       Shai Carmi, Shlomo Havlin, Scott Kirkpatrick, Yuval Shavitt,
       and Eran Shir, PNAS  July 3, 2007   vol. 104  no. 27  11150-11154
       http://www.pnas.org/content/104/27/11150.full
    """
    func = lambda v, k, core_number: core_number[v] <= k
    # HACK These two checks are done in _core_helper, but this function
    # requires k to be one less than the maximum core value instead of
    # just the maximum. Therefore we duplicate the checks here. A better
    # solution should exist...
    if core_number is None:
        core_number = nx.core_number(G)
    if k is None:
        k = max(core_number.values()) - 1
    return _core_helper(G, func, k, core_number)


def k_corona(G, k, core_number=None):
    """Return the k-corona of G.

    The k-corona is the subgraph of nodes in the k-core which have
    exactly k neighbours in the k-core.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph
    k : int
       The order of the corona.
    core_number : dictionary, optional
       Precomputed core numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
       The k-corona subgraph

    Raises
    ------
    NetworkXError
        The k-cornoa is not defined for graphs with self loops or
        parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number

    References
    ----------
    .. [1]  k -core (bootstrap) percolation on complex networks:
       Critical phenomena and nonlocal effects,
       A. V. Goltsev, S. N. Dorogovtsev, and J. F. F. Mendes,
       Phys. Rev. E 73, 056101 (2006)
       http://link.aps.org/doi/10.1103/PhysRevE.73.056101
    """
    func = lambda v, k, c: c[v] == k and sum(1 for w in G[v] if c[w] >= k) == k
    return _core_helper(G, func, k, core_number)
