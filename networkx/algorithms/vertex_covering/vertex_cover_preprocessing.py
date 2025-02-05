"""
Functions for preprocessing the graph before vertex cover
"""

from networkx.algorithms.isolate import isolates, number_of_isolates
from networkx.algorithms.vertex_covering.lp_decomposition import (
    lp_decomposition_vc,
    partial_weighted_lp_decomposition,
)
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "remove_isolated_vertices",
    "deg_one_preprocessing",
    "deg_two_preprocessing",
    "high_degree_vertex_preprocessing",
    "check_bipartite_graph",
    "crown_decomposition_based_preprocessing",
    "lp_decomposition_based_preprocessing",
]


@not_implemented_for("directed")
def remove_isolated_vertices(G, k, vc):
    applied = False
    k_new = k
    g_new = G

    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    if k <= 0:
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )

    isolated_vertices = list(isolates(G))

    if isolated_vertices:
        # remove all isolated vertices from the graph
        g_new.remove_nodes_from(isolated_vertices)
        k_new = k
        applied = True

    return (
        applied,
        g_new,
        k_new,
        to_remove_from_vertex_cover,
        to_add_to_vertex_cover,
        is_k_vc_possible,
    )


@not_implemented_for("directed")
def deg_one_preprocessing(G, k, vc):
    applied = False
    k_new = k
    g_new = G
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    if k <= 0:
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )

    node = None
    for u in G:
        if G.degree(u) == 1:
            node = u
            break

    if node is not None:
        # if there is a degree one vertex, add its neigbour to vertex cover
        # and remove the neighbour from the graph
        # thereby reducing the size of the graph
        neighbour = list(g_new.neighbors(node))[0]

        to_add_to_vertex_cover.add(neighbour)
        g_new.remove_node(neighbour)
        k_new = k - 1

        applied = True

    return (
        applied,
        g_new,
        k_new,
        to_remove_from_vertex_cover,
        to_add_to_vertex_cover,
        is_k_vc_possible,
    )


@not_implemented_for("directed")
def deg_two_preprocessing(G, k, vc):
    pass


@not_implemented_for("directed")
def high_degree_vertex_preprocessing(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    if k <= 0:
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )

    node = None
    for u in G:
        if G.degree(u) >= k + 1:
            # any vertex cover of size atmost k must contain u
            node = u

    if node is not None:
        to_add_to_vertex_cover.add(node)
        g_new.remove_node(node)
        k_new = k - 1
        applied = True

    return (
        applied,
        g_new,
        k_new,
        to_remove_from_vertex_cover,
        to_add_to_vertex_cover,
        is_k_vc_possible,
    )


@not_implemented_for("directed")
def check_bipartite_graph(G, k, vc):
    pass


@not_implemented_for("directed")
def crown_decomposition_based_preprocessing(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    if k <= 0 or len(G) <= 3 * k:
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )


@not_implemented_for("directed")
def lp_decomposition_based_preprocessing(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    if k <= 0 or len(G) <= 2 * k:
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )

    lp_value, greater_than_half, less_than_half, equal_to_half = lp_decomposition_vc(
        G, k
    )

    if lp_value > k:
        # if lp_value is greater than k, then no vc of size atmost k exists
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )

    if len(equal_to_half) == len(G):
        # then all halfs is the unique optimum
        pass

    else:
        # we can add greater_than_half set to the vertex cover
        # and remove union of greater_than_half and less_than_half from the graph
        to_add_to_vertex_cover = greater_than_half
        g_new.remove_nodes_from(greater_than_half.union(less_than_half))
        if len(greater_than_half) > k:
            # then k vc is not possible
            is_k_vc_possible = False
            return (
                applied,
                g_new,
                k_new,
                to_remove_from_vertex_cover,
                to_add_to_vertex_cover,
                is_k_vc_possible,
            )

        k_new = k - len(greater_than_half)
        applied = True
        return (
            applied,
            g_new,
            k_new,
            to_remove_from_vertex_cover,
            to_add_to_vertex_cover,
            is_k_vc_possible,
        )


@not_implemented_for("directed")
def surplus_one_neighbours_not_independent(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    # if there is an edge (u, v) such that solving LPVC(G) with x(u) = x(v) = 1
    # results in a solution with value exactly half greater than the value of the original LPVC(G)

    # since at this point all halfs would be the solution
    original_lp_value = len(G) / 2

    for u, v in G.edges:
        lp_value_new, g_half, l_half, e_half = partial_weighted_lp_decomposition(
            G, {u: 1, v: 1}
        )
        if lp_value_new == original_lp_value + 0.5:
            # set with surplus one is l_half set
            Z = l_half
            N_Z = set()

            for u in Z:
                N_Z.update(G.neighbors(u))

            N_Z.difference_update(Z)

            # we can add N_Z to the vertex cover
            # delete Z union N_Z from the graph and decrease k by |N_Z|
            if len(N_Z) > k:
                is_k_vc_possible = False
                return (
                    applied,
                    g_new,
                    k_new,
                    to_remove_from_vertex_cover,
                    to_add_to_vertex_cover,
                    is_k_vc_possible,
                )

            g_new.remove_nodes_from(Z.union(N_Z))
            k_new = k - len(N_Z)
            applied = True
            to_add_to_vertex_cover = N_Z

            return (
                applied,
                g_new,
                k_new,
                to_remove_from_vertex_cover,
                to_add_to_vertex_cover,
                is_k_vc_possible,
            )

    return (
        applied,
        g_new,
        k_new,
        to_remove_from_vertex_cover,
        to_add_to_vertex_cover,
        is_k_vc_possible,
    )


@not_implemented_for("directed")
def surplus_one_neighbours_independent(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    to_remove_from_vertex_cover = set()
    to_add_to_vertex_cover = set()
    is_k_vc_possible = True

    # if there is a vertex such that solving LPVC(G) with x(u) = 0 results in a solution with value
    # exactly 0.5 greater than the value of original LPVC(G)

    # since at this point all halfs would be the solution
    original_lp_value = len(G) / 2

    for u in G:
        lp_value_new, g_half, l_half, e_half = partial_weighted_lp_decomposition(
            G, {u: 0}
        )
        if lp_value_new == original_lp_value + 0.5:
            # then Z is the l_half set
            # and G has a VC of size atmost k if and only ???

            # set with surplus one is l_half set
            Z = l_half
            N_Z = set()

            for u in Z:
                N_Z.update(G.neighbors(u))

            N_Z.difference_update(Z)
