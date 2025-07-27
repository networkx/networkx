import inspect
from itertools import combinations

import networkx as nx
from networkx.algorithms.fvs.fvs_preprocessing import *
from networkx.algorithms.tree.recognition import is_forest
from networkx.exception import NetworkXPointlessConcept
from networkx.utils.decorators import not_implemented_for

preprocessing_rules = [
    _remove_isolated_vertices,
    _deg_one_preprocessing,
    _remove_self_loops,
    _handling_high_multiplicity,
]

branch_preprocessing_rules = [_handling_cycles, _handling_degree_two_vertex]


# For debugging
def trace(func):
    def wrapper(*args, **kwargs):
        # sig = inspect.signature(func)
        # bound_args = sig.bind(*args, **kwargs)
        # bound_args.apply_defaults()
        #
        # print(f"Function: {func.__name__}")
        # print("Arguments:")
        # for name, value in bound_args.arguments.items():
        #     print(f"  {name} = {value}")
        #
        return func(*args, **kwargs)

    return wrapper


@not_implemented_for("directed")
@trace
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
@trace
def _fvs_disjoint_compression_preprocessing(G, k, X, Y, r_1, fvs):
    is_k_fvs_possible = True

    rules = branch_preprocessing_rules

    applied = False
    for rule in rules:
        if not applied:
            (applied, G, r_new, is_k_fvs_possible, function_to_be_applied) = rule(
                G, k, X, Y, r_1
            )
            k = r_new
            r_1 = r_new

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
            return _fvs_disjoint_compression_preprocessing(G, k, X, Y, r_1, fvs)

    return G, k, fvs, is_k_fvs_possible


@not_implemented_for("directed")
@trace
def _fvs_disjoint_compression_branching(G, k, X, Y, r_1):
    # k and r_1 has to be the same
    if r_1 <= 0:
        is_G_forest = False
        try:
            is_G_forest = is_forest(G)
        except NetworkXPointlessConcept:
            is_G_forest = True
        if is_G_forest:
            return True, set()
        else:
            return False, set()

    is_G_forest = False
    try:
        is_G_forest = is_forest(G)
    except NetworkXPointlessConcept:
        is_G_forest = True

    if is_G_forest or len(G) == 0:
        return True, set()

    fvs = set()
    # Branch preprocessing
    G, k, fvs, is_k_fvs_possible = _fvs_disjoint_compression_preprocessing(
        G, k, X, Y, r_1, fvs
    )
    r_1 = k

    # early return
    if not is_k_fvs_possible:
        return False, set()

    v = None
    # pick a degree 1 vertex (wrt Y)
    for vertex in Y:
        cnt = 0
        for neighbour in G.neighbors(vertex):
            if neighbour in Y:
                cnt += 1
        if cnt <= 1:
            v = vertex
            break

    # v = Y.pop()
    # either v is in the solution or v is not in the solution

    if v is not None and v in Y:
        Y.remove(v)
    # case 1 : v is in the solution
    is_fvs_exists, fvs_sub = _fvs_disjoint_compression_branching(
        G, k - 1, X, Y, r_1 - 1
    )
    if is_fvs_exists:
        fvs.update(fvs_sub)
        fvs.update([v])
        return True, fvs

    # case 2: v is not in the solution
    X.add(v)
    is_fvs_exists, fvs_sub = _fvs_disjoint_compression_branching(G, k, X, Y, r_1)
    # X.discard(v)
    if is_fvs_exists:
        fvs.update(fvs_sub)
        return True, fvs

    # if both return False, k-sized fvs is not possible
    return False, set()


@not_implemented_for("directed")
@trace
def _guess_intersection_and_fvs(G, k, S):
    # returns boolean, k_sized_solution if it exists

    # S is a k + 1 sized solution
    S_nodes = list(S)
    remaining_vertices = set(G).difference(S)

    for subset_length in range(len(S_nodes) + 1):
        # subset length should be less than or equal to k
        if subset_length > k:
            continue

        for S_intersection_R_guess in combinations(S_nodes, subset_length):
            H = G.copy()
            H.remove_nodes_from(S_intersection_R_guess)
            is_H_forest = False
            try:
                is_H_forest = is_forest(H)
            except NetworkXPointlessConcept:
                is_H_forest = True

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
            # print(f"S_intersection_R = {S_intersection_R_guess}")
            is_r_1_fvs_possible, r_1_sized_solution = (
                _fvs_disjoint_compression_branching(
                    H, r - 1, S_minus_R.copy(), remaining_vertices.copy(), r - 1
                )
            )

            if not is_r_1_fvs_possible:
                continue
            return True, r_1_sized_solution

    return False, set()


@not_implemented_for("directed")
@trace
def feedback_vertex_set(G, k):
    r"""Returns a tuple (is_k_fvs_exists, fvs) where `is_k_fvs_exists` is a boolean denoting
    if a feedback vertex set of size at most `k` exists and
    if True, `fvs` denotes a feedback vertex set of size at most `k`
    else fvs is an empty set

    A *feedback vertex set* of a graph is a set of vertices whose removal makes
    the graph acyclic

    Parameters
    ----------
    G : Networkx Graph

    k : integer
        Maximum Size for the Feedback Vertex Set

    Returns
    -------
    is_k_fvs_exists : bool

    fvs : set
        A Feedback Vertex Set for the graph *G* of size at most *k* if one exists
        else an empty set

    Notes
    -----
    This function is the implementation of the parameterized algorithm for feedback vertex set in [2]_ in the chapter ***
    including kernelization procedures

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Feedback_vertex_set

    .. [2] Marek Cygan, Fedor V. Fomin, Lukasz Kowalik, Daniel Lokshtanov, Daniel Marx, Marcin Pilipczuk, Michal Pilipczuk, and Saket Saurabh. 2015. Parameterized Algorithms (1st. ed.). Springer Publishing Company, Incorporated.
    https://dl.acm.org/doi/book/10.5555/2815661#
    """

    if len(G) == 0:
        # return trivial FVS
        return True, set()

    g_new = nx.MultiGraph(G)
    nodes = list(g_new.nodes)
    n = len(nodes)
    if n <= k:
        return True, set(nodes[:k])

    # k + 1 solution for a subgraph of k + 2 vertices
    S = set(nodes[: k + 1])
    H = g_new.subgraph(nodes[: k + 2])
    # print(S)
    # print(H.nodes, H.edges)

    for k_new in range(k + 3, n):
        is_k_fvs_possible, k_sized_solution = _guess_intersection_and_fvs(H, k, S)
        if not is_k_fvs_possible:
            return False, set()
        else:
            # add the new vertex to get the new k + 1 sized solution
            S = k_sized_solution.union([nodes[k_new - 1]])
            H = g_new.subgraph(nodes[:k_new])

    # print(S)
    # print(H.nodes, H.edges)
    is_k_fvs_possible, k_sized_solution = _guess_intersection_and_fvs(H, k, S)
    if not is_k_fvs_possible:
        return False, set()

    return True, k_sized_solution
