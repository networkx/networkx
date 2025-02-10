"""
Function to find vertex cover of size atmost k
"""

from networkx.algorithms.vertex_covering.lp_decomposition import find_lp_decomposition
from networkx.algorithms.vertex_covering.vertex_cover_preprocessing import *
from networkx.utils.decorators import not_implemented_for

preprocessing_rules = [
    remove_isolated_vertices,
    remove_self_loops,
    deg_one_preprocessing,
    deg_two_preprocessing,
    high_degree_vertex_preprocessing,
    check_bipartite_graph,
    crown_decomposition_based_preprocessing,
    lp_decomposition_based_preprocessing,
    surplus_one_neighbours_not_independent,
    surplus_one_neighbours_independent,
]
max_deg_branch_preprocessing_rules = []
vc_above_lp_branch_preprocessing_rules = []


__all__ = [
    "vertex_cover_preprocessing",
    "vertex_cover_branch_preprocessing",
    "vertex_cover_branching",
    "max_degree_branching",
    "vc_above_lp_branching",
    "vertex_cover",
]


@not_implemented_for("directed")
def vertex_cover_preprocessing(G, k, vc, rules=None):
    is_k_vc_possible = True

    if rules is None:
        rules = preprocessing_rules

    applied = False

    for rule in rules:
        if not applied:
            (
                applied,
                G,
                k,
                is_k_vc_possible,
                function_to_be_applied,
            ) = rule(G, k, vc)

            print(applied, rule.__name__, G.edges(), k, vc, is_k_vc_possible)

            if not is_k_vc_possible:
                print("EARLY PREPROCESSING OVER")
                is_k_vc_possible = False
                return G, k, vc, is_k_vc_possible

            # if to_remove_from_vc:
            #     assert isinstance(vc, set)
            #     vc.difference_update(to_remove_from_vc)
            # if to_add_to_vc:
            #     vc.update(to_add_to_vc)

            if applied and function_to_be_applied is not None:
                print(function_to_be_applied.__name__)
                is_k_vc_exists, vc_sub = vertex_cover(G, k)

                if not is_k_vc_exists:
                    is_k_vc_possible = False
                    return G, k, vc, is_k_vc_possible

                vc.update(vc_sub)
                function_to_be_applied(is_k_vc_exists, vc)

        if applied:
            return vertex_cover_preprocessing(G, k, vc)

    print("PREPROCESSING OVER")
    return G, k, vc, is_k_vc_possible
    #
    # while k > 0:
    #     applied = False
    #
    #     for rule in rules:
    #         if not applied:
    #             (
    #                 applied,
    #                 G,
    #                 k,
    #                 to_remove_from_vc,
    #                 to_add_to_vc,
    #                 is_k_vc_possible,
    #                 function_to_be_applied,
    #             ) = rule(G, k, vc)
    #
    #             if not is_k_vc_possible:
    #                 is_k_vc_possible = False
    #                 return G, k, vc, is_k_vc_possible
    #
    #             # if to_remove_from_vc:
    #             #     assert isinstance(vc, set)
    #             #     vc.difference_update(to_remove_from_vc)
    #             # if to_add_to_vc:
    #             #     vc.update(to_add_to_vc)
    #
    #             if applied and function_to_be_applied is not None:
    #                 is_k_vc_exists, vc = vertex_cover(G, k)
    #                 function_to_be_applied(is_k_vc_exists, vc)
    #
    #     if not applied:
    #         break
    #
    # return G, k, vc, is_k_vc_possible
    #


@not_implemented_for("directed")
def vertex_cover_branch_preprocessing(G, k, vc, rules):
    return vertex_cover_preprocessing(G, k, vc, rules=rules)


@not_implemented_for("directed")
def vertex_cover_branching(G, k, rules):
    # rules denotes which algo to use
    # if 1.4656^k, rules will be max_deg_branch_preprocessing_rules
    # if 2.618^(k - lpOpt) rules will be vc_above_lp_branch_preprocessing_rules
    vc = set()
    G, k, vc, is_k_vc_possible = vertex_cover_branch_preprocessing(
        G, k, vc, rules=rules
    )
    # there should not be any isolated vertices

    if not is_k_vc_possible:
        return False, set()

    # base case
    if k <= 0:
        if len(G.edges):
            return False, set()
        else:
            return True, set()

    if len(G) == 0:
        return True, set()

    # branch based on max degree
    max_deg, max_deg_vertex = 0, None

    for u in G:
        deg = G.degree(u)
        if deg > max_deg:
            max_deg = deg
            max_deg_vertex = u

    # max deg vertex will not be None here
    # either max_deg_vertex is in the vertex cover or its neighbours is in the vertex cover

    g_new = G.copy()
    g_new.remove_node(max_deg_vertex)

    is_k_vc_possible, vc_sub = vertex_cover_branching(g_new, k - 1, rules)
    if is_k_vc_possible:
        vc.update(vc_sub)
        vc.update({max_deg_vertex})
        return True, vc

    del g_new

    # else then all its neihbours must be present in the vc
    g_new = G.copy()
    neighbours = g_new.neighbors(max_deg_vertex)

    g_new.remove_node(max_deg_vertex)
    g_new.remove_nodes_from(neighbours)
    # length of neighbours will be atmost k since the graph is preprocessed and
    # high_degree_rule is already present in the preprocessing

    is_k_vc_possible, vc_sub = vertex_cover_branching(g_new, k - len(neighbours), rules)
    if is_k_vc_possible:
        vc.update(vc_sub)
        vc.update(neighbours)
        return True, vc
    else:
        return False, set()


@not_implemented_for("directed")
def max_degree_branching(G, k):
    rules = max_deg_branch_preprocessing_rules
    return vertex_cover_branching(G, k, rules)


@not_implemented_for("directed")
def vc_above_lp_branching(G, k):
    rules = vc_above_lp_branch_preprocessing_rules
    return vertex_cover_branching(G, k, rules)


def vertex_cover(G, k):
    print("ENTRY")
    # find lp-opt value
    # compare 1.4656^k and 2.618^(k - lpOpt)
    if len(G) == 0:
        return True, set()

    g_new = G.copy()

    vc = set()
    g_new, k, vc, is_k_vc_possible = vertex_cover_preprocessing(g_new, k, vc)

    if not is_k_vc_possible:
        print("EARLY RETURN")
        return False, set()

    lp_opt_value, *_ = find_lp_decomposition(g_new)

    if lp_opt_value > k:
        return False, set()

    vc_above_lp_opt_algo_check = 2.618 ** (k - lp_opt_value)
    max_deg_algo_check = 1.4656**k

    is_k_vc_exists, vc_sub = False, set()

    if vc_above_lp_opt_algo_check < max_deg_algo_check:
        is_k_vc_exists, vc_sub = vc_above_lp_branching(g_new, k)
    else:
        is_k_vc_exists, vc_sub = max_degree_branching(g_new, k)

    vc.update(vc_sub)

    return is_k_vc_exists, vc
