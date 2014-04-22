#-*- coding: utf-8 -*-
"""
We use the following definitions:

A forest is an (undirected) graph with no cycles.
A tree is a connected forest.

A directed forest is a directed graph whose underlying graph is a forest.
A directed tree is a (weakly) connected, directed forest.
    Equivalently: It is a directed graph whose underlying graph is a tree.
    Note: Some take the term directed tree to be synonymous with an
        arborescence. We do not follow that convention here.
    Note: Since the underlying graph is a tree, any orientation defines a DAG
        So all directed trees are DAGs. Thus, the definition we use here is,
        in fact, equivalent to a polytree.

A DAG is a directed graph with no directed cycles.
    Example:  A -> B, A -> C, B -> C is a DAG that is not a directed tree.

A polyforest is a DAG that is also a directed forest.
A polytree is a weakly connected polyforest.
    Equivalently, a polytree is a DAG whose underlying graph is a tree.

A branching is a polyforest with each edge directed to a different node.
So the maximum in-degree is, at most, one. The maximum number of edges any
branching can have is n-1. In this case, the branching spans the graph, and
we have an arborescence. It is in this sense that the min/max spanning tree
problem is analogous to the min/max arborescence problem.

An arborescence is a (weakly) connected branching. That is, if you look
at the underlying graph, it is a spanning tree. Additionally, all edges
are directed away from a unique root node, for if you had two nodes with
in-degree zero, then weak connectivity would force some other node
to have in-degree of at least 2 (which is not allowed in branchings).

"""

import networkx as nx

__author__ = """\n""".join([
    'Ferdinando Papale <ferdinando.papale@gmail.com>',
    'chebee7i <chebee7i@gmail.com>',
])


__all__ = ['is_arborescence', 'is_branching', 'is_forest', 'is_tree']

@nx.utils.not_implemented_for('undirected')
def is_arborescence(G):
    """
    Returns `True` if `G` is an arborescence.

    """
    if not is_tree(G):
        return False

    if max(G.in_degree().values()) > 1:
        return False

    return True

@nx.utils.not_implemented_for('undirected')
def is_branching(G):
    """
    Returns `True` if `G` is a branching.

    A branching is a directed forest with maximum in-degree equal to 1.

    Parameters
    ----------
    G : directed graph
        The directed graph to test.

    Returns
    -------
    b : bool
        A boolean that is `True` if `G` is a branching.

    """
    if not is_forest(G):
        return False

    if max(G.in_degree().values()) > 1:
        return False

    return True

def is_forest(G):
    """
    Returns `True` if G is a forest.

    For directed graphs, the direction of edges is ignored, and the graph `G`
    is considered to be a directed forest if the underlying graph is a forest.

    """
    n = G.number_of_nodes()
    if n == 0:
        raise nx.exception.NetworkXPointlessConcept('G has no nodes.')

    if G.is_directed():
        components = nx.weakly_connected_component_subgraphs
    else:
        components = nx.connected_component_subgraphs

    for component in components(G):
        # Make sure the component is a tree.
        if component.number_of_edges() != component.number_of_nodes() - 1:
            return False

    return True

def is_tree(G):
    """
    Returns `True` if `G` is a tree.

    A tree is a simple, connected graph with no cycles.

    For directed graphs, the direction of edges is ignored, and the graph `G`
    is considered to be a directed tree if the underlying graph is a tree.

    Parameters
    ----------
    G : graph
        The graph to test.

    Returns
    -------
    b : bool
        A boolean that is `True` if `G` is a tree.

    Notes
    -----
    Directed trees are also known as polytrees. Sometimes, "directed tree"
    is defined more restrictively to mean "arboresence" instead.

    """
    n = G.number_of_nodes()
    if n == 0:
        raise nx.exception.NetworkXPointlessConcept('G has no nodes.')

    if G.is_directed():
        is_connected = nx.is_weakly_connected
    else:
        is_connected = nx.is_connected

    # A simple, connected graph with no cycles has n-1 edges.

    if G.number_of_edges() != n - 1:
        return False

    return is_connected(G)
