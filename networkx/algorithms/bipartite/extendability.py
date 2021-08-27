""" Provides a function for computing the extendability of a graph which is
undirected, simple, connected and bipartite and contains at least one perfect matching."""


import networkx as nx
from networkx.utils import not_implemented_for


__all__ = ["k_extendability"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def k_extendability(G):
    """Computes the extendability of a graph.

    Definition:
    Graph G is $k$-extendable if and only if G has a perfect matching and every
    set of $k$ independent edges can be extended to a perfect matching in G.

    Definition:
    The extendability of a graph, denoted by ext(G), is defined as the maximum
    $k$ for which G is $k$-extendable.

    Definition:
    Let G be a simple, connected, undirected and bipartite graph with a perfect
    matching M and bipartition (U,V). The residual graph of G, denoted by $G_M$,
    is the graph obtained from G by directing the edges of M from V to U and the
    edges that do not belong to M from U to V.

    Lemma([1]):
    Let M be a perfect matching of G. G is $k$-extendable if and only if its residual
    graph $G_M$ is strongly connected and there are $k$ vertex-disjoint directed
    paths between every vertex of U and every vertex of V.

    Assuming that input graph G is undirected, simple, connected, bipartite and contains
    a perfect matching M is a perfect matching, this function constructs the residual
    graph $G_M$ of G and returns the minimum value among the maximum vertex-disjoint
    directed paths between every vertex of U and every vertex of V in $G_M$. By combining
    the second definition and the lemma, notice that this value represents the extendability
    of the graph G.

    Parameters
    ----------

        G : NetworkX Graph

    Returns
    -------

        extendability: int

    Raises
    ------

        NetworkXError
           If the graph G is not simple.
           If the graph G is disconnected.
           If the graph G is not bipartite.
           If the graph G does not contain a perfect matching.
           If the residual graph of G is not strongly connected.

    Notes
    -----

        Time complexity O($n^3$ $m^2$)) where $n$ is the number of vertices
        and $m$ is the number of edges.

    References
    ----------

        ..[1] "A polynomial algorithm for the extendability problem in bipartite graphs",
              J. Lakhal, L. Litzler, Information Processing Letters, 1998.

    """

    for edge in G.edges:
        if edge[0] == edge[1]:
            raise nx.NetworkXError("Graph G is not simple")

    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph G is not connected")

    if not nx.bipartite.is_bipartite(G):
        raise nx.NetworkXError("Graph G is not bipartite")

    U, V = nx.bipartite.sets(G)

    # Variable $k$ stands for the extendability of graph G
    k = float("Inf")

    maximum_matching = nx.bipartite.hopcroft_karp_matching(G)

    if not nx.is_perfect_matching(G, maximum_matching):
        raise nx.NetworkXError("Graph G does not contain a perfect matching")

    # Construct a list consists of the edges of M by directing them from V to U
    perfect_matching = []
    for vertex in maximum_matching.keys():
        if vertex in V:
            neighbor = maximum_matching[vertex]
            perfect_matching.append((vertex, neighbor))

    # Direct all the edges of G
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

    # Construct the residual graph of G
    residual_G = nx.DiGraph()
    residual_G.add_nodes_from(G.nodes)
    residual_G.add_edges_from(directed_edges)

    if not nx.is_strongly_connected(residual_G):
        raise nx.NetworkXError("The residual graph of G is not strongly connected")

    # Find the maximum number of vertex-disjoint paths between every vertex of U and V and keep the minimum
    for u in U:
        for v in V:
            numb_paths = sum(1 for _ in nx.node_disjoint_paths(residual_G, u, v))
            k = k if k < numb_paths else numb_paths

    return k
