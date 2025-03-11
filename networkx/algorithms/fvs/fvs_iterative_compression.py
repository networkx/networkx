import networkx as nx
from networkx.algorithms.fvs.fvs_preprocessing import *
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
