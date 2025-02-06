"""
Function to find vertex cover of size atmost k
"""

from networkx.utils.decorators import not_implemented_for

preprocessing_rules = []
max_deg_branch_preprocessing_rules = []
vc_above_lp_branch_preprocessing_rules = []


@not_implemented_for("directed")
def vertex_cover_preprocessing(G, k, vc, rules=None):
    is_k_vc_possible = True

    if rules is None:
        rules = preprocessing_rules

    while k > 0:
        applied = False

        for rule in rules:
            if not applied:
                applied, G, k, to_remove_from_vc, to_add_to_vc, is_k_vc_possible = rule(
                    G, k, vc
                )

                if not is_k_vc_possible:
                    is_k_vc_possible = False
                    return G, k, vc, is_k_vc_possible

                if to_remove_from_vc:
                    assert isinstance(vc, set)
                    vc.difference_update(to_remove_from_vc)
                if to_add_to_vc:
                    vc.update(to_add_to_vc)

        if not applied:
            break

    return G, k, vc, is_k_vc_possible


@not_implemented_for("directed")
def vertex_cover_branch_preprocessing(G, k, vc, rules):
    return vertex_cover_preprocessing(G, k, vc, rules=rules)


@not_implemented_for("directed")
def vertex_cover_branching(G, k, rules):
    # rules denotes which algo to use
    # if 1.4656^k, rules will be max_deg_branch_preprocessing_rules
    # if 2.618^(k - lpOpt) rules will be vc_above_lp_branch_preprocessing_rules
    vc = set()
    G, k, vc = vertex_cover_branch_preprocessing(G, k, vc, rules=rules)
    # there should not be any isolated vertices

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
        vc.union(max_deg_vertex)
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
