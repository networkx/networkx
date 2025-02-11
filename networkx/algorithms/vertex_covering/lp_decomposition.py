import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching, to_vertex_cover
from networkx.algorithms.bipartite.basic import sets
from networkx.utils import not_implemented_for

# from .bipartite_get_top_nodes import get_top_nodes

__all__ = ["_lp_decomposition_vc", "_find_lp_decomposition"]


@not_implemented_for("directed")
def _lp_decomposition_vc(G: nx.Graph, k):
    lp_value, greater_than_half, less_than_half, equal_to_half = _find_lp_decomposition(
        G
    )

    if lp_value > k:
        # if lp_value is greater than k, then no vc of size atmost k exists
        return lp_value, greater_than_half, less_than_half, equal_to_half

    if len(G) == len(equal_to_half):
        # trying to find a non all half solution
        for u in G:
            # assign weight for u as zero
            # which automatically implies weight of neighbours of u are 1
            lp_value_new, g_half, l_half, e_half = _partial_weighted_lp_decomposition(
                G, {u: 0}
            )

            if lp_value == lp_value_new:
                return lp_value, g_half, l_half, e_half

            lp_value_new, g_half, l_half, e_half = _partial_weighted_lp_decomposition(
                G, {u: 1}
            )
            if lp_value == lp_value_new:
                return lp_value, g_half, l_half, e_half

    return lp_value, greater_than_half, less_than_half, equal_to_half


@not_implemented_for("directed")
def _partial_weighted_lp_decomposition(G, partial_weights):
    """
    finding lp decomposition subject to the weights following partial_weights
    """
    greater_than_half = set()
    less_than_half = set()

    for u, weight in partial_weights.items():
        if weight < 0.5:
            # if u is assigned weight 0, then all neighbours of u has to assigned weight 1
            less_than_half.add(u)
            greater_than_half.update(G.neighbors(u))

        elif weight > 0.5:
            greater_than_half.add(u)

    g_new = G.copy()
    g_new.remove_nodes_from(greater_than_half.union(less_than_half))

    lp_value, g_half, l_half, e_half = _find_lp_decomposition(g_new)
    return (
        lp_value + len(greater_than_half),
        g_half.union(greater_than_half),
        l_half.union(less_than_half),
        e_half,
    )


@not_implemented_for("directed")
def _find_lp_decomposition(G: nx.Graph):
    """
    Given a graph `G` and a parameter `k`,
    returns a tuple return `lp_value, greater_than_half, less_than_half, equal_to_half`,
    where, in the solution of Linear Programming formulation of Vertex Cover
    `lp_value` is the value of the optimum solution
    `greater_than_half` denotes the set of vertices which got weight more than 0.5,
    `less_than_half` denotes the set of vertices which got weight less than 0.5,
    `equal_to_half` denotes the set of vertices which got weight equal to 0.5,
    """

    if len(G) == 0:
        return 0, set(), set(), set()

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
    coloring = nx.bipartite.color(g_new)
    top_nodes = [key for key, val in coloring.items() if val == 0]
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

    return lp_value, greater_than_half, less_than_half, equal_to_half
