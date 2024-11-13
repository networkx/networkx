import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching
from networkx.algorithms.bipartite.matching import to_vertex_cover
from networkx.utils import not_implemented_for

__all__ = ["crown_decomposition"]


@not_implemented_for("directed")
def crown_decomposition(G: nx.Graph, k: int) -> bool | tuple[set, set, set]:
    """
    Given a graph `G` and a parameter `k`, returns False if matching of size more
    than `k` is found, else returns a crown decomposition (C, H, R) of the graph G

    """

    # it should be ensured in this algorithm that, k does not become negative

    assert len(G) > 3 * k, f"Graph should have more than 3 * k = {3 * k} vertices"

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
                # the loop takes each vertetx from the set of vertices
                # in v_from_maximal_matching and deletes the edges present
                # between this vertex and all vertices
                # present in v_from_maximal_matching

                """
                is it valid to remove edges from G, or should we create a graph copy ?
                """
                G.remove_edge(node, neighbor)

    # now we need to find a maximum matching and a minimum vertex cover of the new graph

    # applying hopcraft karp algorithm
    maximum_matching = hopcroft_karp_matching(G, v_from_maximal_matching)

    if len(maximum_matching) > k:
        return False

    minimum_vertex_cover = to_vertex_cover(
        G, maximum_matching, top_nodes=v_from_maximal_matching
    )

    # this returns a set of minimm vertex cover in this new auxiliary graph

    head_vertices = v_from_maximal_matching.intersection(minimum_vertex_cover)
    crown = set()
    for a in head_vertices:
        crown.add(maximum_matching[a])
    assert len(crown) != 0, "Crown Size is zero"

    rest = graph_nodes.difference(head_vertices.union(crown))

    return (head_vertices, crown, rest)


@not_implemented_for("directed")
def crown_decomposition_vc(
    G: nx.Graph, k: int, vertex_cover_candidate: set
) -> tuple[bool, set]:
    """
    Given a graph `G`, a parameter `k` and a set `vertex_cover_candidate`,
    returns a tuple `(is_crown_decomposition_possible, vertex_cover_candidate)`,
    where `is_crown_decomposition_possible` denotes if further crown decomposition is
    possible and `vertex_cover_candidate` denotes a candidate for vertex cover
    """

    # it should be ensured in this algorithm that, k does not become negative

    if G is None or len(G) == 0:
        return True, vertex_cover_candidate
    if len(G.nodes) < (3 * k + 1):
        return True, vertex_cover_candidate

    is_vc_exist_or_decomposition = crown_decomposition(G, k)
    if is_vc_exist_or_decomposition is False:
        return False, vertex_cover_candidate

    assert isinstance(is_vc_exist_or_decomposition, tuple)
    (head_vertices, crown, rest) = is_vc_exist_or_decomposition

    # delete all the vertices in union of head and crown from the graph
    head_union_crown = head_vertices.union(crown)
    G.remove_nodes_from(head_union_crown)

    vertex_cover_candidate = vertex_cover_candidate.union(head_vertices)

    return crown_decomposition_vc(G, k - len(head_vertices), vertex_cover_candidate)
