#    Copyright(C) 2011-2019 by
#    Jangwon Yie <kleinaberoho10@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:  Jangwon Yie (kleinaberoho10@gmail.com)

"""
Generators for wheel_graph.
"""

import networkx as nx

__all__ = ['wheel_graph']


def wheel_graph(n: int):
    """ Generates a wheel graph.

    In the mathematical discipline of graph theory, a wheel graph is a graph
    formed by connecting a single universal vertex to all vertices of a cycle.
    A wheel graph with n vertices can also be defined as the 1-skeleton of
    an (n-1)-gonal pyramid.

    More information can be found at:
    https://en.wikipedia.org/wiki/Wheel_graph

    Parameters
    ----------
    n : an order of a graph which will be generated.

    Returns
    -------
    G : networkx graph

    Notes
    --------
    A wheel_graph of order n satisfies following properties:
    number of vertices : n
    number of edges : 2(n-1)
    diameter :  2 if n > 4, 1 if n == 4.
    girth : 3
    chromatic number : 3 if n is odd, 4 otherwise
    It is Hamiltonian(https://en.wikipedia.org/wiki/Hamiltonian_path),
    self-dual(https://en.wikipedia.org/wiki/Dual_graph)
    and definitely planar(https://en.wikipedia.org/wiki/Planar_graph).

    Raises
    --------
    :exc:`ValueError`
        if n is not a positive integer.
    """

    if n <= 0:
        raise ValueError('n must be positive.')

    if type(n) != int:
        raise ValueError('n must be an integer.')

    graph = nx.Graph()
    nodes = list(range(1, n+1))
    graph.add_nodes_from(nodes)

    edges_for_cycle = [(i, i+1) for i in range(2, n)]
    edges_for_cycle.append((n, 2))

    edges_from_center = [(1, i) for i in range(2, n+1)]

    graph.add_edges_from(edges_for_cycle)
    graph.add_edges_from(edges_from_center)

    return graph
