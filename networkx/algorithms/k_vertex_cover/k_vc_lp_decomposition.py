import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching, to_vertex_cover
from networkx.utils import not_implemented_for

from .bipartite_get_top_nodes import get_top_nodes

__all__ = ["lp_decomposition_vc"]


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

    # it should be ensured in this algorithm that, k does not become negative
    label = {}
    reverse_label = {}
    label_index = 1
    for node in G.nodes():
        label[node] = label_index
        reverse_label[label_index] = node
        label_index += 1

    g_new = nx.Graph()

    for node in G.nodes():
        g_new.add_node(f"1_{label[node]}")
        g_new.add_node(f"2_{label[node]}")

    for node in G.nodes:
        for neighbor in G.neighbors(node):
            g_new.add_edge(f"1_{label[node]}", f"2_{label[neighbor]}")

    # bipartite graph is created
    weight_dictionary = {}
    top_nodes = get_top_nodes(g_new)
    maximum_matching = hopcroft_karp_matching(g_new, top_nodes=top_nodes)
    min_vertex_cover = to_vertex_cover(g_new, maximum_matching, top_nodes=top_nodes)

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

    lp_value = 0.0

    # iterate through the original graph vertices and add it
    # to the corresponding set
    for node in G.nodes:
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
    """
    Given a graph `G`, a parameter `k` and a set `vertex_cover_candidate`,
    returns a tuple `(is_k_vc_possible, vertex_cover_candidate)` (using LP decomposition),
    where `is_k_vc_possible` is False if k sized vertex cover is not
    possible and `vertex_cover_candidate` denotes a candidate for vertex cover
    """
    # it should be ensured in this algorithm that, k does not become negative
    if G is None or len(G) == 0 or len(G.edges) == 0:
        # Further LP decomposition cannot be applied
        return True, vertex_cover_candidate

    is_vc_exist_or_lp_decomposition = lp_decomposition(G, k)

    if is_vc_exist_or_lp_decomposition is False:
        return False, vertex_cover_candidate

    assert isinstance(is_vc_exist_or_lp_decomposition, tuple)
    (greater_than_half, less_than_half, equal_to_half) = is_vc_exist_or_lp_decomposition

    # delete all the vertices in union of greater_than_half and less_than_half from the graph
    greater_than_half_union_less_than_half = greater_than_half.union(less_than_half)

    if len(greater_than_half_union_less_than_half) > k:
        # if we need to add more than k vertices to the vertex cover
        # then it is a no instance
        # necessary to ensure that k does not become negative
        return False, vertex_cover_candidate
    elif len(greater_than_half_union_less_than_half) == 0:
        # once we all vertices are in equal_to_half set, we are not further decomposing
        # at this stage we can be sure that n <= 2 * k
        return True, vertex_cover_candidate

    # add greater_than_half_union_less_than_half to vertex cover
    # and remove them from graph
    vertex_cover_candidate = vertex_cover_candidate.union(greater_than_half)
    G.remove_nodes_from(greater_than_half_union_less_than_half)

    return lp_decomposition_vc(
        G, k - len(greater_than_half_union_less_than_half), vertex_cover_candidate
    )
