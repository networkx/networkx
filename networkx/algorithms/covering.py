"""
********
Covering
********
"""
#    Copyright (C) 2015 by
#    Nishant Nikhil <nishantiam@gmail.com>
#    All rights reserved.
#    BSD license.

import networkx as nx
from networkx.utils import not_implemented_for, arbitrary_element


@not_implemented_for('directed', 'multigraph')
def min_edge_cover(G):
    """Returns a set of edges which constitute the minimum edge cover of the graph.
    An edge cover of a graph is a set of edges such that every vertex of
    the graph is incident to at least one edge of the set.
    A minimum edge cover is an edge covering of smallest possible size.

    `Edge Cover <https://en.wikipedia.org/wiki/Edge_cover>`_

    A smallest edge cover can be found in polynomial time by finding
    a maximum matching and extending it greedily so that all vertices
    are covered.

    Parameters
    ----------
    G : An undirected, unweighted graph.

    Returns
    -------
    min_cover : set
        The covering is returned as a set, ``min_cover``.
        It contains all the edges of minimum edge cover
        in form of tuples.

    Notes
    -----
    Worst Case runtime of ``nx.max_weight_matching(G, maxcardinality=True)``
    is `O(n^{3})`
    And the greedy extension works in `O(n\log{}n)`
    So worst case run time of the function is `O(n^{3})`.

    Minimum edge cover for bipartite graph can also be found using the
    function present in :mod:`networkx.algorithms.bipartite.covering`
    """
    if nx.number_of_isolates(G) > 0:
        # ``min_cover`` does not exist as there is an isolated vertex
        raise nx.NetworkXException(
            "Graph has a vertex with no edge incident on it, "
            "so no edge cover exists.")

    maximum_matching = nx.max_weight_matching(G, maxcardinality=True)
    # ``min_cover`` is superset of ``maximum_matching``
    min_cover = set(maximum_matching.items())
    # iterate for uncovered nodes
    uncovered_nodes = set(G.nodes()) - set(v for u, v in min_cover)
    for v in uncovered_nodes:
        # Since `v` is uncovered, each edge incident to `v` will join it
        # with a covered node (otherwise, if there were an edge joining
        # uncovered nodes `u` and `v`, the maximum matching algorithm
        # would have found it), so we can choose an arbitrary edge
        # incident to `v`. (This applies only in a simple graph, not a
        # multigraph.)
        #
        # Since the graph is guaranteed to be undirected, we need only
        # add a single orientation of the edge.
        u = arbitrary_element(G[v])
        min_cover.add((u, v))
        min_cover.add((v, u))
    return min_cover


def is_edge_covering(G, cover):
    """Returns True if the set of edges forms an edge cove else returns False
    An edge cover of a graph is a set of edges such that every vertex of
    the graph is incident to at least one edge of the set.

    Given a set of edges, whether it is an edge covering can be decided
    in linear time if we just check whether all nodes of the graph
    has an edge from the set, incident on it.

    Parameters
    ----------
    G : An undirected, unweighted graph.
    cover : set of edges to be checked.

    Returns
    -------
    boolean value : True if the set of edges forms an edge cover

    Notes
    -----
    Worst Case runtime is `O(number of nodes)`
    """
    if len(set(G.nodes()) - set(x[0] for x in cover)) > 0:
        return False
    return True
