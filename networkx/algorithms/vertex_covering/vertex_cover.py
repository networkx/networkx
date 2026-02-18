"""
Function to find vertex cover of size atmost k
"""

# from networkx.algorithms.vertex_covering.lp_decomposition import _find_lp_decomposition
from networkx.algorithms.vertex_covering.vertex_cover_preprocessing import *
from networkx.utils.decorators import not_implemented_for

preprocessing_rules = [
    _remove_isolated_vertices,
    _remove_self_loops,
    _deg_one_preprocessing,
    _deg_two_preprocessing,
    _high_degree_vertex_preprocessing,
    _check_bipartite_graph,
    # _crown_decomposition_based_preprocessing,
    # _lp_decomposition_based_preprocessing,
    # _surplus_one_neighbours_not_independent,
    # _surplus_one_neighbours_independent,
]

max_deg_branch_preprocessing_rules = [
    _remove_isolated_vertices,
    _remove_self_loops,
    _deg_one_preprocessing,
    _deg_two_preprocessing,
]

# vc_above_lp_branch_preprocessing_rules = [
#     _lp_decomposition_based_preprocessing,
#     _surplus_one_neighbours_not_independent,
#     _surplus_one_neighbours_independent,
# ]


__all__ = [
    "_vertex_cover_preprocessing",
    "_vertex_cover_branch_preprocessing",
    "_vertex_cover_branching",
    "_max_degree_branching",
    # "_vc_above_lp_branching",
    "vertex_cover",
]


@not_implemented_for("directed")
def _vertex_cover_preprocessing(G, k, vc, rules=None):
    """
    Given an instance (G, k) of Vertex Cover,
    returns the (G', k', vc, is_k_vc_possible) where
    G' : reduced graph
    k' : reduced parameter
    vc : a subset of a vertex cover of size at most k for the original instance G
    is_k_vc_possible : if False, it means that VC of size at most k is not possible,
                        else, it means that VC of size at most k might or might not exist,

    Preprocessing Rules are applied in order (moving on to a preprocessing rule only
    if all of the previous preprocessing rule does not apply) and stopping once all preprocessing fails

    if `rules` is `None`, the algorithm uses the default set of preprocessing rules
    """
    is_k_vc_possible = True

    if rules is None:
        rules = preprocessing_rules

    # variable to check if any preprocessing rule was applied
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

            if not is_k_vc_possible:
                is_k_vc_possible = False
                return G, k, vc, is_k_vc_possible

            if applied and function_to_be_applied is not None:
                is_k_vc_exists, vc_sub = vertex_cover(G, k)

                if not is_k_vc_exists:
                    is_k_vc_possible = False
                    return G, k, vc, is_k_vc_possible

                vc.update(vc_sub)
                function_to_be_applied(is_k_vc_exists, vc)

        if applied:
            return _vertex_cover_preprocessing(G, k, vc)

    return G, k, vc, is_k_vc_possible


@not_implemented_for("directed")
def _vertex_cover_branch_preprocessing(G, k, vc, rules):
    """
    Preprocessing rules applied in each branching step of the algorithm

    Currently, there are 2 branching algorithms, and the set of branch preprocessing rules
    are different for them, which will be passed as argument to this function
    """
    return _vertex_cover_preprocessing(G, k, vc, rules=rules)


@not_implemented_for("directed")
def _vertex_cover_branching(G, k, rules):
    """
    The parameter `rules` is based on which branching algorithm was chosen

    Let T(k) denote the time complexity of the algorithm chosen

    If T(k) = $O^*(1.4656^k)$, then `rules` will be max_deg_branch_preprocessing_rules
    If T(k) = $O^*(2.618^{k - lpOpt})$, then `rules` will be vc_above_lp_branch_preprocessing_rules
    """
    vc = set()
    G, k, vc, is_k_vc_possible = _vertex_cover_branch_preprocessing(
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
            return True, vc

    if len(G) == 0:
        return True, vc

    # branch based on max degree
    max_deg, max_deg_vertex = -1, None
    g_new = G.copy()

    for u in g_new:
        deg = g_new.degree(u)
        if deg > max_deg:
            max_deg = deg
            max_deg_vertex = u

    # max deg vertex will not be None here
    # either max_deg_vertex is in the vertex cover or its neighbours is in the vertex cover
    g_new.remove_node(max_deg_vertex)

    # print(f"SUB CASE graph = {g_new.edges()}, k = {k - 1}")
    is_k_vc_exists, vc_sub = _vertex_cover_branching(g_new, k - 1, rules)
    # print(f"SUB CASE is_k_vc_exists : {is_k_vc_exists}, vc_sub : {vc_sub}")
    if is_k_vc_exists:
        vc.update(vc_sub)
        vc.update({max_deg_vertex})
        return True, vc

    del g_new

    # else then all its neihbours must be present in the vc
    g_new = G.copy()
    neighbours = list(g_new.neighbors(max_deg_vertex))

    g_new.remove_node(max_deg_vertex)
    g_new.remove_nodes_from(neighbours)
    # length of neighbours will be atmost k since the graph is preprocessed and
    # high_degree_rule is already present in the preprocessing

    if k < len(neighbours):
        return False, set()

    is_k_vc_exists, vc_sub = _vertex_cover_branching(g_new, k - len(neighbours), rules)
    if is_k_vc_exists:
        vc.update(vc_sub)
        vc.update(neighbours)
        return True, vc
    else:
        return False, set()


@not_implemented_for("directed")
def _max_degree_branching(G, k):
    """
    The branching algorigthm with time complexity $O^*(1.4656^k)$

    Reference
    ---------
    .. [1] Section 3.1
    [Marek Cygan, Fedor V. Fomin, Lukasz Kowalik, Daniel Lokshtanov, Daniel Marx, Marcin Pilipczuk, Michal Pilipczuk, and Saket Saurabh. 2015. Parameterized Algorithms (1st. ed.). Springer Publishing Company, Incorporated.](https://doi.org/10.1007/978-3-319-21275-3)
    """
    rules = max_deg_branch_preprocessing_rules
    return _vertex_cover_branching(G, k, rules)


# @not_implemented_for("directed")
# def _vc_above_lp_branching(G, k):
#     """
#     The branching algorigthm with time complexity $O^*(2.618^{k - lpOpt})$
#
#     Reference
#     ---------
#     .. [1] Section 3.4
#     [Marek Cygan, Fedor V. Fomin, Lukasz Kowalik, Daniel Lokshtanov, Daniel Marx, Marcin Pilipczuk, Michal Pilipczuk, and Saket Saurabh. 2015. Parameterized Algorithms (1st. ed.). Springer Publishing Company, Incorporated.](https://doi.org/10.1007/978-3-319-21275-3)
#
#     """
#     rules = vc_above_lp_branch_preprocessing_rules
#     return _vertex_cover_branching(G, k, rules)


def vertex_cover(G, k):
    """ """
    if len(G) == 0:
        # print("EMPTY GRAPH, RETURNING TRIVIAL VERTEX COVER")
        return True, set()

    g_new = G.copy()

    vc = set()
    g_new, k, vc, is_k_vc_possible = _vertex_cover_preprocessing(g_new, k, vc)

    if not is_k_vc_possible:
        # print("EARLY RETURN")
        return False, set()

    # find lp-opt value

    # lp_opt_value, *_ = _find_lp_decomposition(g_new)
    #
    # if lp_opt_value > k:
    #     return False, set()

    # compare 1.4656^k and 2.618^(k - lpOpt)
    # vc_above_lp_opt_algo_check = 2.618 ** (k - lp_opt_value)
    # max_deg_algo_check = 1.4656**k

    is_k_vc_exists, vc_sub = False, set()

    # if vc_above_lp_opt_algo_check < max_deg_algo_check:
    #     # print("VC ABOVE LP BRANCHING")
    #     is_k_vc_exists, vc_sub = _vc_above_lp_branching(g_new, k)
    # else:
    #     # print("MAX DEG BRANCHING")
    #     is_k_vc_exists, vc_sub = _max_degree_branching(g_new, k)
    is_k_vc_exists, vc_sub = _max_degree_branching(g_new, k)

    vc.update(vc_sub)

    return is_k_vc_exists, vc
