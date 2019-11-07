# szeged.py - functions related to the Szeged index of a graph
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions related to the Szeged index of a graph."""
import networkx as nx
from networkx.utils import not_implemented_for
from .shortest_paths import shortest_path_length as spl

__all__ = ['szeged_index']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def szeged_index(g: nx.Graph):
    """Returns the Szeged index of the given graph.

    The *Szeged index* of a graph introduced by Ivan Gutman of the concept of the
    Wiener index, introduced by Harry Wiener.

    Parameters
    ----------
    g : NetworkX graph

    Returns
    -------
    int
        The Szeged index of the graph `g`.

    Notes
    -----
    For an edge e = ij, let n_e(i) be the number of vertices of G being closer
    to i than to j and let n_e(j) be the number of vertices of G lying closer
    to j than to i. The Szeged index of a graph G is defined by that the index
    is sum of the product of n_e(x) and n_e(y) for any e = xy in E(G). Formally,
    szeged(G) = sum([n_e(x) * n_e(y) for e=xy in E(G)])

    More information can be found at:
    https://en.wikipedia.org/wiki/Szeged_index

    """
    if nx.is_connected(g):
        return __szeged_index_for_connected(g)

    components = nx.connected_components(g)
    return sum([__szeged_index_for_connected(g.subgraph(component))
                for component in components])


def __szeged_index_for_connected(g: nx.Graph):
    if len(g.edges) == 0:
        return 0
    return sum(__szeged_value_for_edge(g, edge) for edge in g.edges)


def __szeged_value_for_edge(g: nx.Graph, edge):
    u = edge[0]
    v = edge[1]

    u_dist = {w: dist for w, dist in spl(g, source=u).items()}
    v_dist = {w: dist for w, dist in spl(g, source=v).items()}

    vertices = list(g.nodes)
    vertices.remove(u)
    vertices.remove(v)

    u_index = len([w for w in vertices if u_dist[w] < v_dist[w]])
    v_index = len([w for w in vertices if v_dist[w] < u_dist[w]])

    return u_index * v_index
