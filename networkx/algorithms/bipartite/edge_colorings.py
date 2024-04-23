""" Functions related to Edge Coloring"""

import networkx as nx

__all__ = [
    "edge_coloring",
    "minimum_edge_coloring"
    ]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable(name="bipartite_edge_coloring")
def minimum_edge_coloring(G, top_nodes=None, strategy="kempe-chain"):
    """Returns a minimum edge coloring of the bipartite graph `G`.

    An edge coloring is an assignment of colors to the edges of a graph such
    that no two adjacent edges share the same color. 

    Parameters
    ----------
    G : NetworkX graph
    top_nodes : list, optional
        List of nodes that belong to one node set.
    strategy : str, optional
        The strategy to use for edge coloring. Currently, the following strategies are supported :
        "iterated-matching" :
        "kempe-chain" :
        The default strategy is "kempe-chain".

    Returns
    --------
    edge_colors : dict
        The edge coloring as a dict keyed by edges to integers
        that represent that edge's color.

    References
    -----------
    H. N. Gabow and O. Kariv, “Algorithms for edge coloring bipartite
    graphs,” in Proc. 10th Ann. ACM Symp. Theory of computing. ACM,
    1978, pp. 184–192
    https://dl.acm.org/doi/pdf/10.1145/800133.804346

    Raises
    ------
    AmbiguousSolution
        Raised if the input bipartite graph is disconnected and no `top_nodes`
        parameter is provided to determine the node sets. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.
    """

    if strategy == "iterated-matching":
        # Handle the disconnected Graph case
        if top_nodes is None:
            if not nx.is_connected(G):
                raise nx.AmbiguousSolution(
                    "Disconnected graph: Ambiguous solution for bipartite sets."
                )
            top_nodes, _ = nx.bipartite.sets(G)
        coloring = _iterated_matching_edge_coloring(G, top_nodes)
    else:
        coloring = _kempe_chain_bipartite_edge_coloring(G)

    return coloring

#: This function is simply an alias for :func:`minimum_edge_coloring`.
edge_coloring = minimum_edge_coloring

def _kempe_chain_bipartite_edge_coloring(G):
    """Returns the minimum edge coloring of the bipartite graph `G`.

    This function uses the `procedure-augment` as explained in the (paper)[ https://dl.acm.org/doi/pdf/10.1145/800133.804346] to color the edges of the bipartite
    graph such that no two adjacent edges have the same color. 
    In the `procedure-augment`, an edge denoted as type αβ, between nodes `u` and `v`, is considered. 
    The edge `e` is labeled as type αβ if color α is free at node `u` and color β is free at node `v`. 
    If `e` is of type αβ, an αβ path (from `e`) is a path that starts at one end of `e`, alternates between colors α and β, and achieves maximal length.

    Parameters
    ----------
    G : NetworkX graph
        The input bipartite graph.
    top_nodes : list
        List of nodes that belong to one node set.

    Returns
    -------
    coloring : dict
        The edge coloring represented as a dictionary, where `coloring[e]`
        is the color assigned to edge `e`. Colors are represented as integers.
    """

    # The dictionary represents connections between vertices using colors.
    # Each vertex (key) has color-keyed edges pointing to other vertices.
    # For example, v1 has edges (c1: u1), (c2: u2), etc., indicating connections
    # to u1, u2, etc., with respective colors c1, c2, etc.

    # Find the maximum degree in the graph
    delta = max(deg for node, deg in G.degree)

    colors = set(range(delta))
    coloring = {}

    # Initialize color dictionary for each vertex
    # dictionary of dictionary
    used_colors = {node: {} for node in G.nodes}

    for u, v in G.edges:
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


def _iterated_matching_edge_coloring(G, top_nodes):
    """Returns the minimum edge coloring of the bipartite graph `G`.

    This function uses the `procedure one-color` to color the edges of the bipartite
    graph such that no two adjacent edges have the same color.
    The "one-color" procedure identifies the matching with vertices of maximum degree, 
    subsequently coloring all edges within that matching with a single color. This process iterates by removing the edges of that matching from the graph.

    Parameters
    ----------
    G : NetworkX graph
        The input bipartite graph.
    top_nodes : list
        List of nodes that belong to one node set.

    Returns
    -------
    coloring : dict
        The edge coloring represented as a dictionary, where `coloring[e]`
        is the color assigned to edge `e`. Colors are represented as integers.
    """
    # Dictionary to store the coloring
    coloring = {}

    # Start coloring with i = 0 color
    i = 0

    G1 = G.copy()

    # Continue the loop until there are no more edges in G1
    while G1.edges:
        # Find a saturating matching with maximum degree using a custom function
        matching = _matching_saturating_max_degree(G1, top_nodes)

        # Assign colors to the edges in the matching
        for edge in matching.items():
            coloring[edge] = i

        # Remove the edges in the matching from G1
        G1.remove_edges_from(list(matching.items()))

        # Increment the color counter
        i += 1

    return coloring


def _matching_saturating_max_degree(G, top_nodes=None):
    """Returns a maximum-degree saturating matching in the bipartite graph `G`.

    Parameters
    ----------
    G : NetworkX graph
        The input bipartite graph.
    top_nodes : list, optional
        List of nodes that belong to the top node set.

    Returns
    -------
    matching : dict
        A dictionary representing the maximum-degree saturating matching.
    """
    max_degree = max(deg for node, deg in G.degree)
    max_degree_vertices = {node for node, deg in G.degree if deg == max_degree}

    # two parts of the bipartite graph
    part_a, part_b = nx.bipartite.sets(G, top_nodes)

    # make two different graphs A_major and B_major
    A_major_nodes = (part_a & max_degree_vertices) | part_b
    B_major_nodes = (part_b & max_degree_vertices) | part_a

    A_major = G.subgraph(A_major_nodes)
    B_major = G.subgraph(B_major_nodes)

    top_nodes_A = top_nodes & A_major_nodes
    top_nodes_B = top_nodes & B_major_nodes

    M1 = nx.bipartite.maximum_matching(A_major, top_nodes_A)
    M2 = nx.bipartite.maximum_matching(B_major, top_nodes_B)

    # combine these two matchings
    final_matching = {}
    visited = set()

    for u, v in list(M1.items()) + list(M2.items()):
        if (u, v) in visited:
            continue
        u1 = u
        edges = [(u, v)]
        visited.update([(u, v), (v, u)])
        M = M2

        while v in M and v != u1:
            u, v = v, M[v]
            edges.append((u, v))
            visited.update([(u, v), (v, u)])
            M = M1 if M is M2 else M2

        if v not in M:
            u, v = v, u
            edges = [(u, v)]
            visited.update([(u, v), (v, u)])

            while v in M:
                u, v = v, M[v]
                edges.append((u, v))
                visited.update([(u, v), (v, u)])
                M = M1 if M is M2 else M2

            u, v = edges[0]
            if (len(edges) % 2 == 1) or (
                (u in M1 and M1[u] == v and u in part_a)
                or (u in M2 and M2[u] == v and u in part_b)
            ):
                k = 0
            else:
                k = 1

            for u1, v1 in edges[k::2]:
                final_matching[u1] = v1
                final_matching[v1] = u1
        elif v == u1:
            for u, v in edges[::2]:
                final_matching[u] = v
                final_matching[v] = u
        else:
            raise ValueError("Bleh")

    return final_matching
