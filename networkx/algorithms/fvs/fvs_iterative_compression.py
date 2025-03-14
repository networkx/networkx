from itertools import chain, combinations

import networkx as nx
from networkx.algorithms.fvs.fvs import is_fvs
from networkx.algorithms.fvs.fvs_preprocessing import *
from networkx.algorithms.tree.recognition import is_forest
from networkx.exception import NetworkXNoCycle
from networkx.utils.decorators import not_implemented_for

preprocessing_rules = [
    _remove_isolated_vertices,
    _deg_one_preprocessing,
    _remove_self_loops,
    _handling_high_multiplicity,
]


@not_implemented_for("directed")
def _fvs_preprocessing(G, k, fvs, rules=None):
    is_k_fvs_possible = True

    if rules is None:
        rules = preprocessing_rules

    applied = False
    for rule in rules:
        if not applied:
            (applied, G, k, is_k_fvs_possible, function_to_be_applied) = rule(G, k, fvs)

            if not is_k_fvs_possible:
                is_k_fvs_possible = False
                return G, k, fvs, is_k_fvs_possible

            if applied and function_to_be_applied is not None:
                is_k_fvs_exists, fvs_sub = feedback_vertex_set(G, k)

                if not is_k_fvs_exists:
                    is_k_fvs_possible = False
                    return G, k, fvs, is_k_fvs_possible

                fvs.update(fvs_sub)
                function_to_be_applied(is_k_fvs_exists, fvs)

        if applied:
            return _fvs_preprocessing(G, k, fvs)

    return G, k, fvs, is_k_fvs_possible


@not_implemented_for("directed")
def _fvs_disjoint_compression(G, k, X, Y, r_1):
    pass


@not_implemented_for("directed")
def _guess_intersection_and_fvs(G, k, S):
    # returns boolean, k_sized_solution if it exists

    # S is a k + 1 sized solution
    S_nodes = list(S)
    remaining_vertices = set(G).difference(S_nodes)

    for subset_length in range(len(S_nodes) + 1):
        for S_intersection_R_guess in combinations(S_nodes, subset_length):
            H = G.copy()
            H.remove_nodes_from(S_intersection_R_guess)
            is_H_forest = False
            try:
                is_H_forest = is_forest(H)
            except NetworkXNoCycle:
                is_H_forest = False

            if not is_H_forest:
                # if H is not forest, the guessed subset cannot be intersection with FVS
                continue

            # S_intersection_R_guess is of length k + 1 - r
            H = G.copy()
            H.remove_nodes_from(S_intersection_R_guess)
            S_set = set(S_nodes)
            # S_minus_R = S setminus R
            S_minus_R = S_set.difference(S_intersection_R_guess)
            r = len(S_minus_R)

            # find a FVS of size at most r - 1
            is_r_1_fvs_possible, r_1_sized_solution = _fvs_disjoint_compression(
                H, k, S_minus_R, remaining_vertices, r - 1
            )

            if not is_r_1_fvs_possible:
                continue
            return True, r_1_sized_solution

    return False, set()


@not_implemented_for("directed")
def feedback_vertex_set(G, k):
    """
    Returns a boolean (is_k_fvs_exists, fvs) where `is_k_fvs_exists` denotes
    if a feedback vertex set of size at most `k` exists and
    if it exists, fvs denotes a feedback_vertex_set of size at most `k`
    else fvs is an empty set
    """

    if len(G) == 0:
        # return trivial FVS
        return True, set()

    g_new = G.copy()
    g_new: nx.MultiGraph
    nodes = list(g_new.nodes)
    n = len(nodes)
    if len(g_new) <= k + 1:
        return True, set(nodes[:k])

    # k + 1 solution for a subgraph of k + 2 vertices
    S = nodes[: k + 1]
    H = g_new.subgraph(nodes[: k + 2])

    for k_new in range(k + 3, n):
        is_k_fvs_possible, k_sized_solution = _guess_intersection_and_fvs(H, k, S)
        if not is_k_fvs_possible:
            return False, set()
        else:
            S = k_sized_solution
            H = g_new.subgraph(k_new)

    if is_fvs(G, S):
        return True, S

    return False, set()
