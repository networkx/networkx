""" Functions related to Edge Coloring"""

import networkx as nx
from networkx.generators.classic import null_graph


# @not_implemented_for("multigraph")
@nx._dispatch(name="bipartite_edge_coloring")
def bipartite_edge_coloring(graph, top_nodes=[], strategy=""):
    """
    Returns a valid edge coloring of the bipartite graph `G`.

    An edge coloring is an assignment of colors to the edges of a graph such that no two adjacent edges share the same color. In the case of bipartite graphs, the coloring ensures that no two edges incident on the same node have the same color.


    Parameters:
    -----------
    G : NetworkX graph

    Optional Parameter:
    ------------------
    top_nodes : set with all nodes that belong to one node set
    strategy :

    Returns :
    --------
    edge_colors : dictionary
        The edge coloring is returned as a dictionary, `edge_colors`, such that
        `edge_colors[e]` is the color assigned to edge `e`. Colors are represented
        as integers.

    References:
    -----------
    Harold N.Gabow and Oded Kariv , “Algorithms for edge coloring bipartite graphs”

    Raises
    ------
    NetworkXError
        Raised if the input graph is not bipartite.
    """
    graph = graph.copy()
    if not nx.is_bipartite(graph):
        raise ValueError("Not a Bipartite Graph")

    # Handle the disconnected Graph case
    if not nx.is_connected(graph) and top_nodes == []:
        raise ValueError("Disconnected graph : ambiguous solution ")

    if top_nodes == []:
        top_nodes, b = nx.bipartite.sets(graph)

    # Dictionary to store the coloring
    coloring = {}

    if strategy == "vizing":
        raise NotImplementedError

    # Start coloring with i = 0 color
    i = 0

    while graph.edges:
        matching = _matching_saturating_max_degree(graph.copy(), top_nodes)
        _color_matching_edges(graph, matching, i, coloring)
        graph.remove_edges_from(list(matching.items()))
        i += 1
    return coloring


def _find_max_degree_vertices(graph):
    # Get a dictionary of node degrees
    degrees = dict(graph.degree())

    # Find the maximum degree in the graph
    max_degree = max(degrees.values())

    # Find nodes with the maximum degree
    max_degree_nodes = [
        node for node, degree in degrees.items() if degree == max_degree
    ]

    return max_degree_nodes


def _matching_saturating_max_degree(graph, top_nodes=[]):
    max_degree_vertices = _find_max_degree_vertices(graph)

    # two parts of the bipartite graph
    part_a, part_b = nx.bipartite.sets(graph, top_nodes)

    # make two different graphs A_major and B_major
    A_major_nodes = (part_a & set(max_degree_vertices)) | part_b
    B_major_nodes = (part_b & set(max_degree_vertices)) | part_a

    A_major = graph.subgraph(A_major_nodes)
    B_major = graph.subgraph(B_major_nodes)

    top_nodes_A = list(set(top_nodes) & set(A_major.nodes()))
    top_nodes_B = list(set(top_nodes) & set(B_major.nodes()))
    M1 = nx.bipartite.maximum_matching(A_major, top_nodes_A)
    M2 = nx.bipartite.maximum_matching(B_major, top_nodes_B)

    return _combine_matchings(M1, M2, part_a, part_b)


def _combine_matchings(M1, M2, A, B):
    """
    Combines two Matching M1,M2 using dictionary data structure
    """
    final_matching = {}

    components = _find_components(M1, M2)

    for cycle in components["cycles"]:
        for i in range(0, len(cycle), 2):
            u, v = cycle[i]
            final_matching[u] = v
            final_matching[v] = u

    for path in components["paths"]:
        u, v = path[0]
        if (len(path) % 2 == 1) or (
            (u in M1 and M1[u] == v and u in A) or (u in M2 and M2[u] == v and u in B)
        ):
            k = 0
        else:
            k = 1

        for u1, v1 in path[k::2]:
            final_matching[u1] = v1
            final_matching[v1] = u1

    return final_matching


def _find_components(M1, M2):
    components = {"cycles": [], "paths": []}
    visited = set()

    # while
    for u, v in list(M1.items()) + list(M2.items()):
        if (u, v) in visited:
            continue
        u1 = u
        edges = [(u, v)]
        visited.add((u, v))
        visited.add((v, u))
        M = M2

        while v in M and v != u1:
            u = v
            v = M[v]
            edges.append((u, v))
            visited.add((u, v))
            visited.add((v, u))
            M = M1 if M is M2 else M2

        if v not in M:
            u, v = v, u
            edges = [(u, v)]
            visited.add((u, v))
            visited.add((v, u))

            while v in M:
                u = v
                v = M[v]
                edges.append((u, v))
                visited.add((u, v))
                visited.add((v, u))
                M = M1 if M is M2 else M2

            components["paths"].append(edges)
        elif v == u1:
            components["cycles"].append(edges)
        else:
            raise ValueError("Bleh")

    return components


def _color_matching_edges(graph, matching, color, coloring):
    for u, v in list(matching.items()):
        edge = (u, v) if u != v else (v, u)  # Ensure consistent order for edge
        coloring[edge] = color
        graph[u][v]["color"] = color
