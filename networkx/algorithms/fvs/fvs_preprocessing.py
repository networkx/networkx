import networkx as nx
from networkx.algorithms.isolate import isolates
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "_remove_isolated_vertices",
    "_deg_one_preprocessing",
    "_remove_self_loops",
    "_handling_high_multiplicity",
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

    def function_to_be_applied_after_self_loops(is_k_fvs_exists, f):
        if not is_k_fvs_exists:
            return
        f.update([self_loop_node])

    return (
        applied,
        g_new,
        k_new,
        is_k_fvs_possible,
        function_to_be_applied_after_self_loops,
    )


@not_implemented_for("directed")
def _handling_high_multiplicity(G, k, fvs):
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
def _disjoint_compression_preprocessing(G, k, fvs):
    pass
