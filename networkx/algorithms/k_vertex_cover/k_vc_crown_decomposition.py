import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching
from networkx.utils import not_implemented_for

__all__ = ["crown_decomposition"]


@not_implemented_for("directed")
def crown_decomposition(G: nx.Graph, k: int) -> bool | list[set]:
    maximal_matching = nx.maximal_matching(G)
    if len(maximal_matching) > k:
        return False

    v_from_maximal_matching = set()
    for a, b in maximal_matching:
        v_from_maximal_matching.add(a)
        v_from_maximal_matching.add(b)
    # v_from_maximal_matching consists of the nodes in one side of the new auxiliary bi partite graphs

    graph_nodes = set(G.nodes)
    indepedent_set = graph_nodes.difference(v_from_maximal_matching)
    for node in v_from_maximal_matching:
        for neighbor in G.neighbors(node):
            if neighbor in v_from_maximal_matching:
                G.remove_edge(node, neighbor)
                # the loop takes each vertetx from the set of vertices
                # in v_from_maximal_matching and deletes the edges present
                # between this vertex and all vertices
                # present in v_from_maximal_matching

    # now we need to find a maximum matching and a minimum vertex cover of the new graph

    # applying hopcraft karp algorithm
    maximum_matching = hopcroft_karp_matching(G, v_from_maximal_matching)

    if len(maximum_matching) > k:
        return False

    minimum_vertex_cover = nx.to_vertex_cover(
        G, maximum_matching, top_nodes=v_from_maximal_matching
    )

    # this returns a set of minimm vertex cover in this new auxiliary graph

    head_vertices = v_from_maximal_matching.intersection(minimum_vertex_cover)
    crown = set()
    for a in head_vertices:
        crown.add(maximum_matching[a])
    assert len(crown) != 0, "Crown Size is zero"

    rest = graph_nodes.difference(head_vertices.union(crown))

    return [head_vertices, crown, rest]


@not_implemented_for("directed")
def crown_decomposition_vc(
    G: nx.Graph, k: int, vertex_cover_candidate: set
) -> tuple[bool, set]:
    if G is None:
        return True, vertex_cover_candidate
    if len(G.nodes) < (3 * k + 1):
        return True, vertex_cover_candidate
    maximal_matching = nx.maximal_matching(G)

    is_vc_exist_or_decomposition = crown_decomposition(G, k)
    if is_vc_exist_or_decomposition is False:
        return False, vertex_cover_candidate

    assert isinstance(is_vc_exist_or_decomposition, list)
    [head_vertices, crown, rest] = is_vc_exist_or_decomposition

    head_union_crown = head_vertices.union(crown)
    G.remove_nodes_from(head_union_crown)

    # delete all the vertices in union of head and crown from the graph

    vertex_cover_candidate = vertex_cover_candidate.union(head_vertices)

    return crown_decomposition_vc(G, k - len(head_vertices), vertex_cover_candidate)
