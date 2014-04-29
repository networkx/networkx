# -*- coding: utf-8 -*-
"""
utils for connectivity package
"""
import networkx as nx

__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])

__all__ = ['build_auxiliary_node_connectivity',
           'build_auxiliary_edge_connectivity']


def build_auxiliary_node_connectivity(G, nodelist=None):
    r"""Creates a directed graph D from an undirected graph G to compute flow
    based node connectivity.

    For an undirected graph G having `n` nodes and `m` edges we derive a
    directed graph D with 2n nodes and 2m+n arcs by replacing each
    original node `v` with two nodes `vA`,`vB` linked by an (internal)
    arc in D. Then for each edge (u,v) in G we add two arcs (uB,vA)
    and (vB,uA) in D. Finally we set the attribute capacity = 1 for each
    arc in D [1].

    For a directed graph having `n` nodes and `m` arcs we derive a
    directed graph D with 2n nodes and m+n arcs by replacing each
    original node `v` with two nodes `vA`,`vB` linked by an (internal)
    arc `(vA,vB)` in D. Then for each arc (u,v) in G we add one arc (uB,vA)
    in D. Finally we set the attribute capacity = 1 for each arc in D.

    References
    ----------
    .. [1] Kammer, Frank and Hanjo Taubig. Graph Connectivity. in Brandes and
        Erlebach, 'Network Analysis: Methodological Foundations', Lecture
        Notes in Computer Science, Volume 3418, Springer-Verlag, 2005.
        http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf

    """
    directed = G.is_directed()

    mapping = {}
    D = nx.DiGraph()
    if nodelist is None:
        nodelist = G
    for i,node in enumerate(nodelist):
        mapping[node] = i
        D.add_node('%dA' % i,id=node)
        D.add_node('%dB' % i,id=node)
        D.add_edge('%dA' % i, '%dB' % i, capacity=1)

    edges = []
    for (source, target) in G.edges():
        edges.append(('%sB' % mapping[source], '%sA' % mapping[target]))
        if not directed:
            edges.append(('%sB' % mapping[target], '%sA' % mapping[source]))

    D.add_edges_from(edges, capacity=1)
    return D, mapping


def build_auxiliary_edge_connectivity(G):
    """Auxiliary digraph for computing flow based edge connectivity

    If the input graph is undirected, we replace each edge (u,v) with
    two reciprocal arcs (u,v) and (v,u) and then we set the attribute
    'capacity' for each arc to 1. If the input graph is directed we simply
    add the 'capacity' attribute. Part of algorithm 1 in [1]_ .

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms. (this is a
        chapter, look for the reference of the book).
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
    """
    if G.is_directed():
        if nx.get_edge_attributes(G, 'capacity'):
            return G
        D = G.copy()
        capacity = dict((e,1) for e in D.edges())
        nx.set_edge_attributes(D, 'capacity', capacity)
        return D
    else:
        D = G.to_directed()
        capacity = dict((e,1) for e in D.edges())
        nx.set_edge_attributes(D, 'capacity', capacity)
        return D
