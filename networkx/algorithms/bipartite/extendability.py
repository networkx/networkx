""" Provides a function for computing the extendability of
graph which is undirected, simple, connected and bipartite.

For example:

>> nodes = ['1', '2', '3', '4',
            '5', '6', '7', '8']
>> edges = [('1', '5'), ('1', '6'), ('1', '7'),
            ('2', '5'), ('2', '6'), ('2', '8'),
            ('3', '6'), ('3', '7'), ('3', '8'),
            ('4', '5'), ('4', '7'), ('4', '8')]
>> graph = nx.Graph()
>> graph.add_nodes_from(nodes)
>> graph.add_edges_from(edges)
>> find_extendability(graph)
2

"""


import networkx as nx
from networkx.utils import not_implemented_for


__all__ = [
    "find_extendability",
]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def find_extendability(G):
    """Computes the extendability of a graph.

    Definition
    Graph G is $k$-extendable if and only if G has a perfect matching and every
    set of $k$ independent edges can extend to perfect matching.

    EXTENDABILITY PROBLEM
    --------------------------------------------
    Input: A graph G and a positive integer $k$.
    Output: Is G $k$-extendable?
    --------------------------------------------

    In general case the above problem is co-NP-complete([2]).
    If graph G is bipartite, then it can be decided in polynomial time([1]).

    The maximization version of the EXTENDABILITY PROBLEM asks to compute the
    maximum $k$ for which G is $k$-extendable.

    Let G be a simple, connected, undirected and bipartite graph with a perfect
    matching M and bipartition (U,V). The residual graph of G, denoted by $G_M$,
    is the graph obtained from G by directing the edges of M from V to U and the
    edges that do not belong to M from U to V.

    Lemma([1])
    Let M be a perfect matching of G. G is k-extendable if and only if its residual
    graph $G_M$ is strongly connected and there are $k$ vertex-disjoint directed
    paths between every vertex of U and every vertex of V.

    Parameters
    ----------
    G : NetworkX Graph
    ----------

    Returns
    -------
    extendability: int
    -------

    Raises
    ------
    NetworkXError
      If the graph G is of type nx.MultiGraph, nx.MultiDiGraph or nx.DiGraph.
      If the graph G is not simple.
      If the graph G is disconnected.
      If the graph G is not bipartite.
      If the graph G does not contain a perfect matching.
      If the residual graph of G is not strongly connected.
    ------

    Notes
    -----
    Time complexity: O($n^3$ $m^2$))
    -----

    References
    ----------
    ..[1] "A polynomial algorithm for the extendability problem in bipartite graphs",
      J. Lakhal, L. Litzler, Information Processing Letters, 1998.
    ..[2] "The matching extension problem in general graphs is co-NP-complete",
      Jan Hackfeld, Arie M. C. A. Koster, Springer Nature, 2018.

    """
    # Graph G must be simple and undirected
    for edge in G.edges:
        if edge[0] == edge[1]:
            raise nx.NetworkXError("Graph G is not simple")
    # Graph G must be connected
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph G is not connected")
    # Graph G must be bipartite
    if not nx.bipartite.is_bipartite(G):
        raise nx.NetworkXError("Graph G is not bipartite")
    # Obtain the two sets which form the partition of graph G
    U, V = nx.bipartite.sets(G)
    # Variable $k$ stands for the extendability of graph G
    k = float("Inf")
    # Find a maximum matching
    maximum_matching = nx.bipartite.hopcroft_karp_matching(G)
    # Check whether G has a perfect matching or not
    if nx.is_perfect_matching(G, maximum_matching):
        # Convert undirected graph G into a directed graph G'
        directed_G = nx.DiGraph()
        # Obtain the edges of the perfect matching from the dictionary
        perfect_matching = []
        for vertex in maximum_matching.keys():
            # Store only the edges from V to U
            if vertex in V:
                neighbor = maximum_matching[vertex]
                perfect_matching.append((vertex, neighbor))
        # Direct the edges
        directed_edges = []
        for edge in G.edges:
            first_coordinate, second_coordinate = edge[0], edge[1]
            reverse_pair = (second_coordinate, first_coordinate)
            if first_coordinate in U and second_coordinate in V:
                if reverse_pair in perfect_matching:
                    directed_edges.append(reverse_pair)
                else:
                    directed_edges.append(edge)
            if first_coordinate in V and second_coordinate in U:
                if edge in perfect_matching:
                    directed_edges.append(edge)
                else:
                    directed_edges.append(reverse_pair)
        directed_G.add_nodes_from(G.nodes)
        directed_G.add_edges_from(directed_edges)
        # Check whether G' is strongly connected or not
        if nx.is_strongly_connected(directed_G):
            # Find the number of maximum disjoint paths between every vertex of U and V and keep the minimum
            for u in U:
                for v in V:
                    vertex_disjoint_paths = []
                    paths = nx.node_disjoint_paths(directed_G, u, v)
                    for path in paths:
                        vertex_disjoint_paths.append(path)
                    k = min(k, len(vertex_disjoint_paths))
        else:
            raise nx.NetworkXError("The residual graph of G is not strongly connected")
    else:
        raise nx.NetworkXError("Graph G does not contain a perfect matching")
    return k
