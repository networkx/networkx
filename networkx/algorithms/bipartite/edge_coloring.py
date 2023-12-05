""" Functions related to Edge Coloring"""

import networkx as nx

__all__ = [
    "bipartite_edge_coloring",
    "kempe_chain_bipartite_edge_coloring",
    "iterated_matching_edge_coloring",
]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatch(name="bipartite_edge_coloring")
def bipartite_edge_coloring(G, top_nodes=None, strategy="kempe-chain"):
    """Returns a valid edge coloring of the bipartite graph `G`.

    An edge coloring is an assignment of colors to the edges of a graph such
    that no two adjacent edges share the same color. In the case of bipartite
    graphs, the coloring ensures that no two edges incident on the same node
    have the same color.

    Two strategies:
    --------------
    iterated_matching
    kempe_chain

    Parameters:
    -----------
    G : NetworkX graph

    Optional Parameter:
    ------------------
    top_nodes : list, optional
        List of nodes that belong to one node set.
    strategy : str, optional
        The strategy to use for edge coloring. Currently, the following strategies are supported :
        "iterated-matching" :
        "kempe-chain" :
        The default strategy is "kempe-chain".

    Returns :
    --------
    edge_colors : dict
        The edge coloring is returned as a dictionary, `edge_colors`, such that
        `edge_colors[e]` is the color assigned to edge `e`. Colors are represented
        as integers.

    References:
    -----------
    H. N. Gabow and O. Kariv, “Algorithms for edge coloring bipartite
    graphs,” in Proc. 10th Ann. ACM Symp. Theory of computing. ACM,
    1978, pp. 184–192
    https://dl.acm.org/doi/pdf/10.1145/800133.804346
    Raises
    ------
    NetworkXError
        Raised if the input graph is not bipartite.

    AmbiguousSolution
      Raised if the input bipartite graph is disconnected and no container
      with all nodes in one bipartite set is provided. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.
    """
    G = G.copy()
    if not nx.is_bipartite(G):
        raise nx.NetworkXError("Not a Bipartite Graph")

    if strategy == "iterated-matching":
        # Handle the disconnected Graph case
        if not nx.is_connected(G) and top_nodes is None:
            raise nx.AmbiguousSolution(
                "Disconnected graph: Ambiguous solution for bipartite sets."
            )

        if top_nodes is None:
            top_nodes, _ = nx.bipartite.sets(G)
        coloring = iterated_matching_edge_coloring(G, top_nodes)
    else:
        coloring = kempe_chain_bipartite_edge_coloring(G)

    return coloring


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatch(name="kempe_chain_bipartite_edge_coloring")
def kempe_chain_bipartite_edge_coloring(G):
    """Returns the minimum edge coloring of the bipartite graph `graph`.

    This function uses the procedure augment to color the edges of the bipartite
    graph such that no two adjacent edges have the same color.

    Parameters:
    -----------
    G : NetworkX graph
        The input bipartite graph.
    top_nodes : list
        List of nodes that belong to one node set.

    Returns:
    --------
    coloring : dict
        The edge coloring represented as a dictionary, where `coloring[e]`
        is the color assigned to edge `e`. Colors are represented as integers.
    """

    # The dictionary represents connections between vertices using colors.
    # Each vertex (key) has color-keyed edges pointing to other vertices.
    # For example, v1 has edges (c1: u1), (c2: u2), etc., indicating connections
    # to u1, u2, etc., with respective colors c1, c2, etc.

    # Get a dictionary of node degrees
    degrees = dict(G.degree())

    # Find the maximum degree in the graph
    delta = max(degrees.values())

    colors = set(range(delta))
    coloring = {}

    # Initialize color dictionary for each vertex
    # dictionary of dictionary
    used_colors = {node: {} for node in G.nodes}

    for edge in G.edges:
        u, v = edge
        # Get the colors of edges ending at u and v
        u_colors = set(used_colors[u].keys())
        v_colors = set(used_colors[v].keys())

        # Take the union and subtract from the color pallete
        available_colors = colors - (u_colors | v_colors)

        if available_colors:
            # Color the edge with the lowest available color
            color = min(available_colors)
            used_colors[u][color] = v
            used_colors[v][color] = u
            coloring[(u, v)] = color
            coloring[(v, u)] = color
        else:
            u_color = next(iter(colors - set(used_colors[u])))
            v_color = next(iter(colors - set(used_colors[v])))
            u1 = u
            v1 = v
            color = v_color

            # Find a Kempe chain and swap colors
            while True:
                used_colors[v1][color] = u1
                coloring[(u1, v1)] = color
                coloring[(v1, u1)] = color
                if color not in used_colors[u1]:
                    used_colors[u1][color] = v1
                    color = v_color if color == u_color else u_color
                    used_colors[u1].pop(color)
                    break
                u_new = used_colors[u1][color]
                used_colors[u1][color] = v1
                v1 = u1
                u1 = u_new
                color = v_color if color == u_color else u_color

    return coloring


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatch(name="iterated_matching_edge_coloring")
def iterated_matching_edge_coloring(G, top_nodes):
    """Returns the minimum edge coloring of the bipartite graph `graph`.

    This function uses the procedure one-color to color the edges of the bipartite
    graph such that no two adjacent edges have the same color.

    Parameters:
    -----------
    graph : NetworkX graph
        The input bipartite graph.
    top_nodes : list
        List of nodes that belong to one node set.

    Returns:
    --------
    coloring : dict
        The edge coloring represented as a dictionary, where `coloring[e]`
        is the color assigned to edge `e`. Colors are represented as integers.
    """
    # Dictionary to store the coloring
    coloring = {}

    # Start coloring with i = 0 color
    i = 0

    while G.edges:
        matching = _matching_saturating_max_degree(G.copy(), top_nodes)
        _color_matching_edges(G, matching, i, coloring)
        G.remove_edges_from(list(matching.items()))
        i += 1
    return coloring


def _color_matching_edges(G, matching, color, coloring):
    """function used to color the edges of the matching with `color`"""
    for u, v in list(matching.items()):
        edge = (u, v) if u != v else (v, u)  # Ensure consistent order for edge
        coloring[edge] = color


def _find_max_degree_vertices(G):
    """Returns the vertices with the maximum degree in the graph.

    Parameters:
    -----------
    G : NetworkX graph
        The input graph.

    Returns:
    --------
    max_degree_nodes : list
        List of nodes with the maximum degree in the graph.
    """
    # Get a dictionary of node degrees
    degrees = dict(G.degree())

    # Find the maximum degree in the graph
    max_degree = max(degrees.values())

    # Find nodes with the maximum degree
    max_degree_nodes = [
        node for node, degree in degrees.items() if degree == max_degree
    ]

    return max_degree_nodes


def _matching_saturating_max_degree(G, top_nodes=[]):
    """Returns a maximum-degree saturating matching in the bipartite graph `graph`.

    Parameters:
    -----------
    G : NetworkX graph
        The input bipartite graph.
    top_nodes : list, optional
        List of nodes that belong to the top node set.

    Returns:
    --------
    matching : dict
        A dictionary representing the maximum-degree saturating matching.
    """
    max_degree_vertices = _find_max_degree_vertices(G)

    # two parts of the bipartite graph
    part_a, part_b = nx.bipartite.sets(G, top_nodes)

    # make two different graphs A_major and B_major
    A_major_nodes = (part_a & set(max_degree_vertices)) | part_b
    B_major_nodes = (part_b & set(max_degree_vertices)) | part_a

    A_major = G.subgraph(A_major_nodes)
    B_major = G.subgraph(B_major_nodes)

    top_nodes_A = list(set(top_nodes) & set(A_major.nodes()))
    top_nodes_B = list(set(top_nodes) & set(B_major.nodes()))
    M1 = nx.bipartite.maximum_matching(A_major, top_nodes_A)
    M2 = nx.bipartite.maximum_matching(B_major, top_nodes_B)

    return _combine_matchings(M1, M2, part_a, part_b)


def _combine_matchings(M1, M2, A, B):
    """Combines two matchings `M1` and `M2` in the bipartite graph.

    Parameters:
    -----------
    M1 : dict
        Dictionary representing the first matching.
    M2 : dict
        Dictionary representing the second matching.
    A : set
        Set of nodes in the first part of the bipartite graph.
    B : set
        Set of nodes in the second part of the bipartite graph.

    Returns:
    --------
    final_matching : dict
        A dictionary representing the combined matching.
    """
    final_matching = {}
    visited = set()

    # while
    for u, v in list(M1.items()) + list(M2.items()):
        if (u, v) in visited:
            continue
        u1 = u
        edges = [(u, v)]
        visited.update([(u, v), (v, u)])
        M = M2

        while v in M and v != u1:
            u = v
            v = M[v]
            edges.append((u, v))
            visited.update([(u, v), (v, u)])
            M = M1 if M is M2 else M2

        if v not in M:
            u, v = v, u
            edges = [(u, v)]
            visited.update([(u, v), (v, u)])

            while v in M:
                u = v
                v = M[v]
                edges.append((u, v))
                visited.update([(u, v), (v, u)])
                M = M1 if M is M2 else M2

            u, v = edges[0]
            if (len(edges) % 2 == 1) or (
                (u in M1 and M1[u] == v and u in A)
                or (u in M2 and M2[u] == v and u in B)
            ):
                k = 0
            else:
                k = 1

            for u1, v1 in edges[k::2]:
                final_matching[u1] = v1
                final_matching[v1] = u1
        elif v == u1:
            for i in range(0, len(edges), 2):
                u, v = edges[i]
                final_matching[u] = v
                final_matching[v] = u

        else:
            raise ValueError("Bleh")

    return final_matching