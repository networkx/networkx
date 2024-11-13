import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching, to_vertex_cover
from networkx.utils import not_implemented_for

__all__ = ["lp_decomposition"]


@not_implemented_for("directed")
def lp_decomposition(G: nx.Graph, k: int) -> bool | tuple[set, set, set]:
    """
    Given a graph `G` and a parameter `k`, returns False if vertex cover of size atmost `k`
    doesn't exists, else returns a tuple return `(greater_than_half, less_than_half, equal_to_half)`,
    where, in the solution of Linear Programming formulation of Vertex Cover
    `greater_than_half` denotes the set of vertices which got weight more than 0.5,
    `less_than_half` denotes the set of vertices which got weight less than 0.5,
    `equal_to_half` denotes the set of vertices which got weight equal to 0.5
    """

    label = {}
    reverse_label = {}
    label_index = 1
    for node in G.nodes():
        label[node] = label_index
        reverse_label[label_index] = node
    g_new = nx.Graph()

    for node in G.nodes():
        g_new.add_node(f"1_{label[node]}")
        g_new.add_node(f"2_{label[node]}")

    for node in G.nodes:
        for neighbor in G.neighbors(node):
            g_new.add_edge(f"1_{label[node]}", f"2_{label[neighbor]}")

    # bipartite graph is created
    weight_dictionary = {}
    maximum_matching = hopcroft_karp_matching(g_new)
    min_vertex_cover = to_vertex_cover(g_new, maximum_matching)

    for node in G.nodes:
        container_1_name = f"1_{label[node]}"
        container_2_name = f"2_{label[node]}"

        weight = 0.0

        if container_1_name in min_vertex_cover:
            weight += 0.5
        if container_2_name in min_vertex_cover:
            weight += 0.5

        weight_dictionary[node] = weight

    greater_than_half = set()
    less_than_half = set()
    equal_to_half = set()

    lp_value = 0

    for node in min_vertex_cover:
        node_weight = weight_dictionary[node]
        lp_value += node_weight

        if node_weight > 0.5:
            greater_than_half.add(node)
        elif node_weight < 0.5:
            less_than_half.add(node)
        else:
            equal_to_half.add(node)

    if lp_value > k:
        return False

    return (greater_than_half, less_than_half, equal_to_half)


@not_implemented_for("directed")
def lp_decomposition_vc(
    G: nx.Graph, k: int, vertex_cover_candidate: set
) -> tuple[bool, set]:
    """ """
    if G is None or len(G) == 0:
        return True, vertex_cover_candidate

    is_vc_exist_or_lp_decomposition = lp_decomposition_vc(G, k)

    if is_vc_exist_or_lp_decomposition is False:
        return False, vertex_cover_candidate

    assert isinstance(is_vc_exist_or_lp_decomposition, list)
    [greater_than_half, less_than_half, equal_to_half] = is_vc_exist_or_lp_decomposition

    # there exists a min vertex cover including greater_than_half and
    # excluding less_than_half
    G.remove_nodes_from(less_than_half)

    return lp_decomposition(G, k, vertex_cover_candidate)
