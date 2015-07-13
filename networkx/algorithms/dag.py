# -*- coding: utf-8 -*-
from fractions import gcd
import heapq
import networkx as nx
from networkx.utils.decorators import *
from networkx.utils import consume
"""Algorithms for directed acyclic graphs (DAGs)."""
#    Copyright (C) 2006-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
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
    des = set(nx.shortest_path_length(G, source=source).keys()) - set([source])
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
    anc = set(nx.shortest_path_length(G, target=source).keys()) - set([source])
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
        is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort exists
        and a NetworkXUnfeasible exception is raised.

    Notes
    -----
    This algorithm is based on a description and proof in
    Introduction to algorithms - a creative approach [1]_ .

    See also
    --------
    lexicographical_topological_sort

    References
    ----------
    .. [1] Manber, U. (1989). Introduction to algorithms - a creative approach. Addison-Wesley.
        http://www.amazon.com/Introduction-Algorithms-A-Creative-Approach/dp/0201120372
    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "Topological sort not defined on undirected graphs.")

    # nonrecursive version
    indegree_map = {node: len(G.pred[node])
                    for node in G}

    # These nodes have zero indegree and ready to be returned.
    zero_indegree = [node
                     for node, indegree in indegree_map.items()
                     if indegree == 0]

    for node in zero_indegree:
        del indegree_map[node]

    while zero_indegree:
        node = zero_indegree.pop()

        try:
            children = G[node]
        except KeyError:
            raise RuntimeError("Graph changed during iteration")
        for child in children:
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


def lexicographical_topological_sort(G, key=(lambda x: x)):
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
        is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort exists
        and a NetworkXUnfeasible exception is raised.

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

    def create_tuple(node):
        return key(node), node

    indegree_map = dict(G.in_degree())

    # These nodes have zero indegree and are ready to be returned.
    zero_indegree = [create_tuple(node)
                     for node, indegree in indegree_map.items()
                     if indegree == 0]
    heapq.heapify(zero_indegree)

    for _, node in zero_indegree:
        del indegree_map[node]

    while zero_indegree:
        _, node = heapq.heappop(zero_indegree)

        try:
            children = G[node]
        except KeyError:
            raise RuntimeError("Graph changed during iteration")
        for child in children:
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

    s = next(G.nodes_iter())
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
    TC.add_nodes_from(G.nodes_iter())
    TC.add_edges_from(G.edges_iter())
    for v in G:
        TC.add_edges_from((v, u) for u in nx.dfs_preorder_nodes(G, source=v)
                          if v != u)
    return TC


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
    antichains_stacks = [([], list(nx.topological_sort(G)))]
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
def dag_longest_path(G):
    """Returns the longest path in a DAG

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

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
    dist = {}  # stores [node, distance] pair
    for node in nx.topological_sort(G):
        # pairs of dist,node for all incoming edges
        pairs = [(dist[v][0] + 1, v) for v in G.pred[node]]
        if pairs:
            dist[node] = max(pairs)
        else:
            dist[node] = (0, node)
    node, (length, _) = max(dist.items(), key=lambda x: x[1])
    path = []
    while length > 0:
        path.append(node)
        length, node = dist[node]
    return list(reversed(path))


@not_implemented_for('undirected')
def dag_longest_path_length(G):
    """Returns the longest path length in a DAG

    Parameters
    ----------
    G : NetworkX DiGraph
        Graph

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
    path_length = len(nx.dag_longest_path(G)) - 1
    return path_length
