"""
Function to get the k-sized vertex cover
"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["k_vertex_cover", "k_vertex_cover_given_candidate"]


@not_implemented_for("directed")
def max_deg_vertex(G: nx.Graph):
    """
    Returns tuple of (v, max_deg) where max_deg is the maximum degree
    of the graph G and v is the vertex with the degree max_deg
    """
    if len(G) == 0:
        return 0, None

    max_deg = 0
    arg_max_deg = None
    for node in G:
        current_degree = G.degree(node)
        if current_degree > max_deg:
            max_deg = current_degree
            arg_max_deg = node

    return arg_max_deg, max_deg


@not_implemented_for("directed")
def k_vc_preprocessing(G: nx.Graph, k: int, vertex_cover_candidate: set):
    """
    Preprocessing the graph to reduce the given instance into possibly a smaller instance
    """

    while k > 0:
        # remove isolated vertices
        for node in list(G):
            if G.degree(node) == 0:
                G.remove_node(node)

        high_deg_vertex = None
        # check if there is a vertex with degree >= k + 1, if so add it to vertex_cover_candidate
        for node in G:
            if G.degree(node) >= k + 1:
                high_deg_vertex = node
                vertex_cover_candidate.add(node)
                k -= 1
                # G.remove_node(node)
                break

        if high_deg_vertex is not None:
            G.remove_node(high_deg_vertex)
            continue

        if k <= 0:
            break

        # degree 1 vertices
        deg_one_vertex = None
        for node in G:
            if G.degree(node) == 1:
                deg_one_vertex = node
                break

        if deg_one_vertex is None:
            break

        neighbour = list(G.neighbors(deg_one_vertex))[0]

        # add the neighbour to vertex_cover_candidate and reduce the parameter by 1
        vertex_cover_candidate.add(neighbour)
        k -= 1

        G.remove_node(neighbour)
        G.remove_node(deg_one_vertex)

        init_k_size = len(vertex_cover_candidate)
        vertex_cover_candidate = crown_decomposition(G, k, vertex_cover_candidate)[1]
        k = k - (len(vertex_cover_candidate) - init_k_size)

        # NOT SURE IF THE BELOW IS CORRECT YET
        # init_k_size = len(vertex_cover_candidate)
        # vertex_cover_candidate = crown_decomposition(G, k, vertex_cover_candidate)[1]
        # k = k - (len(vertex_cover_candidate) - init_k_size)


def dfs_update_vc(
    u, G: nx.Graph, vertex_cover_candidate: set, mark: bool, visited: set
):
    if u in visited:
        return

    if mark:
        vertex_cover_candidate.add(u)

    visited.add(u)

    for neighbour in G.neighbors(u):
        if neighbour in visited:
            continue
        dfs_update_vc(neighbour, G, vertex_cover_candidate, not mark, visited)


def update_vertex_cover(component: set, G: nx.Graph, vertex_cover_candidate: set):
    assert len(component) > 0, "Empty component"

    start_vertex = None
    for v in component:
        start_vertex = v
        break

    sub_G = G.subgraph(component)
    visited = set()

    if len(sub_G) == len(sub_G.edges()):
        # means it is cycle
        dfs_update_vc(start_vertex, sub_G, vertex_cover_candidate, True, visited)
    else:
        # means it is a linear path
        dfs_update_vc(start_vertex, sub_G, vertex_cover_candidate, False, visited)


@not_implemented_for("directed")
def k_vertex_cover_given_candidate(G: nx.Graph, k: int, vertex_cover_candidate: set):
    # empty graph / edgeless graph
    if len(G) == 0 or len(G.edges) == 0:
        return True

    # graph still has edges
    if k <= 0:
        return False

    # pre-processing
    k_vc_preprocessing(G, k, vertex_cover_candidate)

    # branching on maximum degree vertex
    u, max_deg = max_deg_vertex(G)
    # since graph is not edgeless, one vertex will be returned by the
    # above function
    assert u is not None

    if max_deg <= 2:
        # odd/even cycle or odd/even length path
        # isolated vertices will not be present since those have been preprocessed
        remaining_components = nx.connected_components(G)

        min_vertices_to_be_added = 0

        for component in remaining_components:
            # remaining_components is a generator, can only be traversed once
            min_vertices_to_be_added += math.ceil(len(component) / 2.0)
            update_vertex_cover(component, G, vertex_cover_candidate)

        if min_vertices_to_be_added > k:
            return False

        return True

    vertex_cover_candidate.add(u)
    G_copy = G.copy()
    G_copy.remove_node(u)

    is_k_vc_cover_exist = k_vc(G_copy, k - 1, vertex_cover_candidate)

    if is_k_vc_cover_exist:
        return True

    del G_copy

    vertex_cover_candidate.remove(u)
    G_copy = G.copy()

    # all neighbours of u must be in VC
    neighbours = list(G.neighbors(u))
    num_neighbours = len(neighbours)

    if num_neighbours > k:
        # not possible to add all neighbours since k is less
        # than the number of neighbours
        return False

    for neighbour in neighbours:
        vertex_cover_candidate.add(neighbour)
        G_copy.remove_node(neighbour)

    is_k_vc_cover_exist = k_vc(G_copy, k - num_neighbours, vertex_cover_candidate)

    return is_k_vc_cover_exist


@not_implemented_for("directed")
def k_vertex_cover(G: nx.Graph, k: int):
    """
    returns a tuple (is_k_vc_exist, vertex_cover) where
    is_k_vc_exist is a boolean representing if a VC of size atmost kexists
    and if it exists vertex_cover is a VC of size atmost k
    """

    # components = nx.connected_components(g)
    # component_graphs = [g.subgraph(list(component)) for component in components]
    vertex_cover_candidate = set()

    if nx.is_bipartite(G):
        max_matching = hopcroft_karp_matching(G)
        # the below is the min vertex cover for the bipartite graph
        vertex_cover_bipartite = to_vertex_cover(G, max_matching)
        if k < len(vertex_cover_bipartite):
            return False, set()

        return True, vertex_cover_bipartite

    G_copy = G.copy()
    k_vc_preprocessing(G_copy, k, vertex_cover_candidate)

    # after preprocessing, if G_copy has a vertex cover of size <= k,
    # then the number of edges and vertices will be bounded
    # E(G_copy) <= k^2
    # V(G_copy) <= k^2 + k

    if len(G) == 0 or len(G.edges) == 0:
        return True, vertex_cover_candidate

    if k < 0:
        return False, vertex_cover_candidate

    if len(G_copy.edges) > k**2 or len(G_copy) > k * (k + 1):
        return False, vertex_cover_candidate

    is_k_vc_cover_exist = k_vertex_cover_given_candidate(
        G_copy, k, vertex_cover_candidate
    )
    if is_k_vc_cover_exist:
        return True, vertex_cover_candidate
