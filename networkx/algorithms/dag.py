# -*- coding: utf-8 -*-
"""Algorithms for directed acyclic graphs (DAGs)."""
#    Copyright (C) 2006-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from fractions import gcd
import heapq

import networkx as nx
from networkx.utils import consume, arbitrary_element, pairwise
from networkx.utils.decorators import *

__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                            'Dan Schult (dschult@colgate.edu)',
                            'Ben Edwards (bedwards@cs.unm.edu)',
                            'Neil Girdhar (neil.girdhar@mcgill.ca)'])
__all__ = ['descendants',
           'ancestors',
           'topological_sort',
           'lexicographical_topological_sort',
           'is_directed_acyclic_graph',
           'is_aperiodic',
           'transitive_closure',
           'transitive_reduction',
           'antichains',
           'dag_longest_path',
           'dag_longest_path_length']


def descendants(G, source):
    """Return all nodes reachable from `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G

    Returns
    -------
    des : set()
        The descendants of source in G
    """
    if not G.has_node(source):
        raise nx.NetworkXError("The node %s is not in the graph." % source)
    des = set(n for n, d in nx.shortest_path_length(G, source=source)) - set([source])
    return des


def ancestors(G, source):
    """Return all nodes having a path to `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G

    Returns
    -------
    ancestors : set()
        The ancestors of source in G
    """
    if not G.has_node(source):
        raise nx.NetworkXError("The node %s is not in the graph." % source)
    anc = set(n for n, d in nx.shortest_path_length(G, target=source)) - set([source])
    return anc


def is_directed_acyclic_graph(G):
    """Return True if the graph G is a directed acyclic graph (DAG) or
    False if not.

    Parameters
    ----------
    G : NetworkX graph
        A graph

    Returns
    -------
    is_dag : bool
        True if G is a DAG, false otherwise
    """
    if not G.is_directed():
        return False
    try:
        consume(topological_sort(G))
        return True
    except nx.NetworkXUnfeasible:
        return False


def topological_sort(G):
    """Return a generator of nodes in topologically sorted order.

    A topological sort is a nonunique permutation of the nodes such that an
    edge from u to v implies that u appears before v in the topological sort
    order.

    Parameters
    ----------
    G : NetworkX digraph
        A directed graph

    Returns
    -------
    topologically_sorted_nodes : iterable
        An iterable of node names in topological sorted order.

    Raises
    ------
    NetworkXError
        Topological sort is defined for directed graphs only. If the graph G
        is undirected, a :exc:`NetworkXError` is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort exists
        and a NetworkXUnfeasible exception is raised.  This can also be
        raised if G is changed while the returned iterator is being processed.

    RuntimeError
        If G is changed while the returned iterator is being processed.

    Examples
    --------
    To get the reverse order of the topological sort::

        >>> DG = nx.DiGraph([(1, 2), (2, 3)])
        >>> list(reversed(list(nx.topological_sort(DG))))
        [3, 2, 1]

    Notes
    -----
    This algorithm is based on a description and proof in
    Introduction to algorithms - a creative approach [1]_ .

    See also
    --------
    is_directed_acyclic_graph, lexicographical_topological_sort

    References
    ----------
    .. [1] Manber, U. (1989). Introduction to algorithms - a creative approach. Addison-Wesley.
        http://www.amazon.com/Introduction-Algorithms-A-Creative-Approach/dp/0201120372
    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "Topological sort not defined on undirected graphs.")

    indegree_map = {v: d for v, d in G.in_degree() if d > 0}
    # These nodes have zero indegree and ready to be returned.
    zero_indegree = [v for v, d in G.in_degree() if d == 0]

    while zero_indegree:
        node = zero_indegree.pop()
        if node not in G:
            raise RuntimeError("Graph changed during iteration")
        for _, child in G.edges(node):
            try:
                indegree_map[child] -= 1
            except KeyError:
                raise RuntimeError("Graph changed during iteration")
            if indegree_map[child] == 0:
                zero_indegree.append(child)
                del indegree_map[child]

        yield node

    if indegree_map:
        raise nx.NetworkXUnfeasible("Graph contains a cycle or graph changed "
                                    "during iteration")


def lexicographical_topological_sort(G, key=None):
    """Return a generator of nodes in lexicographically topologically sorted
    order.

    A topological sort is a nonunique permutation of the nodes such that an
    edge from u to v implies that u appears before v in the topological sort
    order.

    Parameters
    ----------
    G : NetworkX digraph
        A directed graph

    key : function, optional
        This function maps nodes to keys with which to resolve ambiguities in
        the sort order.  Defaults to the identity function.

    Returns
    -------
    lexicographically_topologically_sorted_nodes : iterable
        An iterable of node names in lexicographical topological sort order.

    Raises
    ------
    NetworkXError
        Topological sort is defined for directed graphs only. If the graph G
        is undirected, a :exc:`NetworkXError` is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort exists
        and a NetworkXUnfeasible exception is raised.  This can also be
        raised if G is changed while the returned iterator is being processed.

    RuntimeError
        If G is changed while the returned iterator is being processed.

    Notes
    -----
    This algorithm is based on a description and proof in
    Introduction to algorithms - a creative approach [1]_ .

    See also
    --------
    topological_sort

    References
    ----------
    .. [1] Manber, U. (1989). Introduction to algorithms - a creative approach. Addison-Wesley.
        http://www.amazon.com/Introduction-Algorithms-A-Creative-Approach/dp/0201120372
    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "Topological sort not defined on undirected graphs.")

    if key is None:
        key = lambda x: x

    def create_tuple(node):
        return key(node), node

    indegree_map = {v: d for v, d in G.in_degree() if d > 0}
    # These nodes have zero indegree and ready to be returned.
    zero_indegree = [create_tuple(v) for v, d in G.in_degree() if d == 0]
    heapq.heapify(zero_indegree)

    while zero_indegree:
        _, node = heapq.heappop(zero_indegree)

        if node not in G:
            raise RuntimeError("Graph changed during iteration")
        for _, child in G.edges(node):
            try:
                indegree_map[child] -= 1
            except KeyError:
                raise RuntimeError("Graph changed during iteration")
            if indegree_map[child] == 0:
                heapq.heappush(zero_indegree, create_tuple(child))
                del indegree_map[child]

        yield node

    if indegree_map:
        raise nx.NetworkXUnfeasible("Graph contains a cycle or graph changed "
                                    "during iteration")


def is_aperiodic(G):
    """Return True if G is aperiodic.

    A directed graph is aperiodic if there is no integer k > 1 that
    divides the length of every cycle in the graph.

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    Returns
    -------
    aperiodic : boolean
        True if the graph is aperiodic False otherwise

    Raises
    ------
    NetworkXError
        If G is not directed

    Notes
    -----
    This uses the method outlined in [1]_, which runs in O(m) time
    given m edges in G. Note that a graph is not aperiodic if it is
    acyclic as every integer trivial divides length 0 cycles.

    References
    ----------
    .. [1] Jarvis, J. P.; Shier, D. R. (1996),
       Graph-theoretic analysis of finite Markov chains,
       in Shier, D. R.; Wallenius, K. T., Applied Mathematical Modeling:
       A Multidisciplinary Approach, CRC Press.
    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "is_aperiodic not defined for undirected graphs")

    s = arbitrary_element(G)
    levels = {s: 0}
    this_level = [s]
    g = 0
    l = 1
    while this_level:
        next_level = []
        for u in this_level:
            for v in G[u]:
                if v in levels:  # Non-Tree Edge
                    g = gcd(g, levels[u] - levels[v] + 1)
                else:  # Tree Edge
                    next_level.append(v)
                    levels[v] = l
        this_level = next_level
        l += 1
    if len(levels) == len(G):  # All nodes in tree
        return g == 1
    else:
        return g == 1 and nx.is_aperiodic(G.subgraph(set(G) - set(levels)))


@not_implemented_for('undirected')
def transitive_closure(G):
    """ Returns transitive closure of a directed graph

    The transitive closure of G = (V,E) is a graph G+ = (V,E+) such that
    for all v,w in V there is an edge (v,w) in E+ if and only if there
    is a non-null path from v to w in G.

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    Returns
    -------
    TC : NetworkX DiGraph
        Graph

    Raises
    ------
    NetworkXNotImplemented
        If G is not directed

    References
    ----------
    .. [1] http://www.ics.uci.edu/~eppstein/PADS/PartialOrder.py

    """
    TC = nx.DiGraph()
    TC.add_nodes_from(G.nodes())
    TC.add_edges_from(G.edges())
    for v in G:
        TC.add_edges_from((v, u) for u in nx.dfs_preorder_nodes(G, source=v)
                          if v != u)
    return TC


@not_implemented_for('undirected')
def transitive_reduction(G):
    """ Returns transitive reduction of a directed graph

    The transitive reduction of G = (V,E) is a graph G- = (V,E-) such that
    for all v,w in V there is an edge (v,w) in E- if and only if (v,w) is
    in E and there is no path from v to w in G with length greater than 1.

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    Returns
    -------
    TR : NetworkX DiGraph
        Graph

    Raises
    ------
    NetworkXError
        If G is not a directed acyclic graph (DAG) transitive reduction is
        not uniquely defined and a NetworkXError exception is raised.

    References 
    ----------
    https://en.wikipedia.org/wiki/Transitive_reduction

    """   
    if not is_directed_acyclic_graph(G):
        raise nx.NetworkXError(
            "Transitive reduction only uniquely defined on directed acyclic graphs.") 
    TR = nx.DiGraph()
    TR.add_nodes_from(G.nodes())
    for u in G:
        u_edges = set(G[u])
        for v in G[u]:
            u_edges -= {y for x, y in nx.dfs_edges(G, v)}
        TR.add_edges_from((u,v) for v in u_edges)
    return TR


@not_implemented_for('undirected')
def antichains(G):
    """Generates antichains from a DAG.

    An antichain is a subset of a partially ordered set such that any
    two elements in the subset are incomparable.

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    Returns
    -------
    antichain : generator object

    Raises
    ------
    NetworkXNotImplemented
        If G is not directed

    NetworkXUnfeasible
        If G contains a cycle

    Notes
    -----
    This function was originally developed by Peter Jipsen and Franco Saliola
    for the SAGE project. It's included in NetworkX with permission from the
    authors. Original SAGE code at:

    https://sage.informatik.uni-goettingen.de/src/combinat/posets/hasse_diagram.py

    References
    ----------
    .. [1] Free Lattices, by R. Freese, J. Jezek and J. B. Nation,
       AMS, Vol 42, 1995, p. 226.
    """
    TC = nx.transitive_closure(G)
    antichains_stacks = [([], list(reversed(list(nx.topological_sort(G)))))]
    while antichains_stacks:
        (antichain, stack) = antichains_stacks.pop()
        # Invariant:
        #  - the elements of antichain are independent
        #  - the elements of stack are independent from those of antichain
        yield antichain
        while stack:
            x = stack.pop()
            new_antichain = antichain + [x]
            new_stack = [
                t for t in stack if not ((t in TC[x]) or (x in TC[t]))]
            antichains_stacks.append((new_antichain, new_stack))


@not_implemented_for('undirected')
def dag_longest_path(G, weight='weight', default_weight=1):
    """Returns the longest path in a DAG
    If G has edges with 'weight' attribute the edge data are used as weight values.

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    weight : string (default 'weight')
        Edge data key to use for weight

    default_weight : integer (default 1)
        The weight of edges that do not have a weight attribute

    Returns
    -------
    path : list
        Longest path

    Raises
    ------
    NetworkXNotImplemented
        If G is not directed

    See also
    --------
    dag_longest_path_length
    """
    dist = {} # stores {v : (length, u)}
    for v in nx.topological_sort(G):
        us = [(dist[u][0] + data.get(weight, default_weight), u)
            for u, data in G.pred[v].items()]
        # Use the best predecessor if there is one and its distance is non-negative, otherwise terminate.
        maxu = max(us, key=lambda x: x[0]) if us else (0, v)
        dist[v] = maxu if maxu[0] >= 0 else (0, v)
    u = None
    v = max(dist, key=lambda x: dist[x][0])
    path = []
    while u != v:
        path.append(v)
        u = v
        v = dist[v][1]
    path.reverse()
    return path


@not_implemented_for('undirected')
def dag_longest_path_length(G, weight='weight', default_weight=1):
    """Returns the longest path length in a DAG

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

    weight : string (default 'weight')
        Edge data key to use for weight

    default_weight : integer (default 1)
        The weight of edges that do not have a weight attribute

    Returns
    -------
    path_length : int
        Longest path length

    Raises
    ------
    NetworkXNotImplemented
        If G is not directed

    See also
    --------
    dag_longest_path
    """
    path = nx.dag_longest_path(G, weight, default_weight)
    path_length = 0
    for (u, v) in pairwise(path):
        path_length += G[u][v].get(weight, default_weight)

    return path_length
