import networkx as nx
from networkx.algorithms.cycles import find_cycle
from networkx.algorithms.isolate import isolates
from networkx.exception import NetworkXNoCycle
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "_remove_isolated_vertices",
    "_deg_one_preprocessing",
    "_remove_self_loops",
    "_handling_high_multiplicity",
    "_handling_cycles",
    "_handling_degree_two_vertex",
]


@not_implemented_for("directed")
def _remove_isolated_vertices(G, k, f):
    applied = False
    k_new = k
    g_new = G

    is_k_fvs_possible = True

    if k <= 0:
        return (applied, g_new, k_new, is_k_fvs_possible, None)

    isolated_vertices = list(isolates(G))

    if isolated_vertices:
        g_new.remove_nodes_from(isolated_vertices)
        applied = True

    def function_to_be_applied_after_isolated_vertices(is_k_fvs_exists, f):
        if not is_k_fvs_exists:
            return
        # no need to add isolated vertices
        return

    return (
        applied,
        g_new,
        k_new,
        is_k_fvs_possible,
        function_to_be_applied_after_isolated_vertices,
    )


@not_implemented_for("directed")
def _deg_one_preprocessing(G, k, f):
    applied = False
    k_new = k
    g_new = G
    is_k_fvs_possible = True

    node = None
    for u in G:
        if G.degree(u) == 1:
            node = u
            break

    if node is None or k <= 0:
        return (applied, g_new, k_new, is_k_fvs_possible, None)

    function_to_be_applied_after_deg_one = None

    g_new.remove_node(node)
    applied = True

    return (
        applied,
        g_new,
        k_new,
        is_k_fvs_possible,
        function_to_be_applied_after_deg_one,
    )


@not_implemented_for("directed")
def _remove_self_loops(G, k, f):
    applied = False
    k_new = k
    g_new = G
    is_k_fvs_possible = True
    self_loop_node = None

    g_new: nx.MultiGraph

    for u, neighbour_dictionary in g_new.adjacency():
        if u in neighbour_dictionary:
            self_loop_node = u
            break

    if self_loop_node is None:
        return applied, g_new, k_new, is_k_fvs_possible, None

    if k <= 0:
        is_k_fvs_possible = False
        return applied, g_new, k_new, is_k_fvs_possible, None

    g_new.remove_node(self_loop_node)
    k_new = k - 1
    applied = True

    def function_to_be_applied_after_self_loops(is_k_fvs_exists, fvs):
        if not is_k_fvs_exists:
            return
        fvs.update([self_loop_node])

    return (
        applied,
        g_new,
        k_new,
        is_k_fvs_possible,
        function_to_be_applied_after_self_loops,
    )


@not_implemented_for("directed")
def _handling_high_multiplicity(G, k, f):
    applied = False
    g_new = G
    k_new = k
    is_k_fvs_possible = True

    high_multiplicity_edge = None
    for u, v in g_new.edges(keys=False):
        edge_keys = list(G[u][v].keys())

        if len(edge_keys) > 2:
            high_multiplicity_edge = (u, v)
            break

    if high_multiplicity_edge is None:
        return applied, g_new, k_new, is_k_fvs_possible, None

    if k <= 0:
        # high_multiplicity_edge is not None
        # means one of the vertices must be in fvs, but k <= 0, hence
        # not possible
        is_k_fvs_possible = False
        return applied, g_new, k_new, is_k_fvs_possible, None

    u, v = high_multiplicity_edge
    for key in list(g_new[u][v].keys())[2:]:
        g_new.remove_edge(u, v, key)
        applied = True

    return applied, g_new, k_new, is_k_fvs_possible, None


@not_implemented_for("directed")
def _handling_cycles(G, k, X, Y, r_1):
    applied = False
    g_new = G
    r_new = r_1
    is_r_1_fvs_possible = True

    node = None
    for v in Y:
        try:
            _ = find_cycle(g_new, v)
            node = v

        except NetworkXNoCycle:
            continue

    if node is None:
        return applied, g_new, r_new, is_r_1_fvs_possible, None

    if r_1 <= 0:
        is_r_1_fvs_possible = False
        return applied, g_new, r_new, is_r_1_fvs_possible, None

    g_new.remove_node(node)
    applied = True
    r_new = r_1 - 1

    def function_to_be_applied_after_handling_cycles(is_k_fvs_exists, fvs):
        if not is_k_fvs_exists:
            return

        fvs.update([node])

    return (
        applied,
        g_new,
        r_new,
        is_r_1_fvs_possible,
        function_to_be_applied_after_handling_cycles,
    )


@not_implemented_for("directed")
def _handling_degree_two_vertex(G, k, X, Y, r_1):
    applied = False
    g_new = G
    r_new = r_1
    is_r_1_fvs_possible = True

    function_to_be_applied_after_degree_two = None

    node = None
    for v in G:
        if G.degree(v) == 2:
            node = v
            break

    if node is None or r_1 <= 0:
        return (
            applied,
            g_new,
            r_new,
            is_r_1_fvs_possible,
            function_to_be_applied_after_degree_two,
        )

    u, v = list(G.neighbors(node))
    G.add_edge(u, v)
    G.remove_node(node)
    applied = True
    # neighbors = list(G.neighbors(node))
    # multiplicity = len(G.edges(node))
    # G.add_edges_from([(neighbors[0], neighbors[1]) for _ in range(multiplicity)])
    # G.remove_node(node)

    return (
        applied,
        g_new,
        r_new,
        is_r_1_fvs_possible,
        function_to_be_applied_after_degree_two,
    )
