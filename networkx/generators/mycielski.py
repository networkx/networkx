#    Copyright (C) 2010-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

"""Functions related to the Mycielski Operation and the Mycielskian family
of graphs.

"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['mycielskian, mycielski_graph']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def mycielskian(G, iterations=1):
    r"""Returns the Mycielskian of a simple, undirected graph G

    The Mycielskian of graph preserves a graph's triangle free
    property while increasing the chromatic number by 1.

    The Mycielski Operation on a graph, `G=(V,E)`, constructs a new graph
    of size `2|V|+1` with `3|E|+|V|` edges.

    The construction is as follows:

    Let `V = {0, ..., n-1}`. Construct another vertex set `U = {n, ..., 2n}`
    and a vertex, `w = 2n+1`. Construct a new graph, `M`, with vertices
    `U ∪ V ∪ w`.
    For edges, `(u,v)`, in `E` add edges `(u,v), (u, v+n), (u+n, v)` to M.
    Finally, for all vertices `u` in U, add edge `(u,w)` to M.

    The Mycielski Operation can be done multiple times by repeating the above
    process iteratively.

    More information can be found at https://en.wikipedia.org/wiki/Mycielskian

    Parameters
    ----------
    G : graph
        A simple, undirected NetworkX graph
    iterations : int
        The number of iterations of the Mycielski operation to
        preform on G. Defaults to 1. Must be a non-negative integer.

    Returns
    -------
    M : graph
        The Mycielskian of G after the specified number of iterations.

    Notes
    ------
    Graph, node, and edge data are not necessarily propagated to the new graph.

    """

    n = G.number_of_nodes()
    M = nx.convert_node_labels_to_integers(G)

    for i in range(iterations):
        n = M.number_of_nodes()
        M.add_nodes_from(range(n, 2*n))
        old_edges = list(M.edges())
        M.add_edges_from((u, v+n) for u, v in old_edges)
        M.add_edges_from((u+n, v) for u, v in old_edges)
        M.add_node(2*n)
        M.add_edges_from((u+n, 2*n) for u in range(n))

    return M


def mycielski_graph(n):
    """Generator for the n_th Mycielski Graph.

    The Mycielski family of graphs is an infinite set of graphs,
    starting with the singleton graph and with the n_th graph being
    the result of the Mycielski Operation being performed n times on
    the singleton graph. 

    Parameters
    ----------
    n : int
        The desired Mycielski Graph.

    Returns
    -------
    M : graph
        The n_th Mycielski Graph

    """

    if n < 0:
        raise nx.NetworkXError("must satisfy n >= 0")

    return mycielskian(nx.singleton_graph(), n)