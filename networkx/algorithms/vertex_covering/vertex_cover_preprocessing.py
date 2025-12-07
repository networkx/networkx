"""
Functions for preprocessing the graph before vertex cover
"""

import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching, to_vertex_cover
from networkx.algorithms.isolate import isolates, number_of_isolates

# from networkx.algorithms.vertex_covering.crown_decomposition import _crown_decomposition
# from networkx.algorithms.vertex_covering.lp_decomposition import (
#     _lp_decomposition_vc,
#     _partial_weighted_lp_decomposition,
# )
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "_remove_isolated_vertices",
    "_remove_self_loops",
    "_deg_one_preprocessing",
    "_deg_two_preprocessing",
    "_high_degree_vertex_preprocessing",
    "_check_bipartite_graph",
    # "_crown_decomposition_based_preprocessing",
    # "_lp_decomposition_based_preprocessing",
    # "_surplus_one_neighbours_not_independent",
    # "_surplus_one_neighbours_independent",
]

"""
This file contains preprocessing rules for Vertex Cover

All the functions have the same signature

The parameters are
G : nx.Graph
k : int (parameter)
vc : a vertex cover which is a subset of a k-sized vertex cover

And it returns
applied : bool, denoting if the preprocessing rule was applied
g_new : Reduced Graph
k_new : Reduced Parameter
is_k_vc_possible : if False, it means that VC of size at most k is not possible,
                    else, it means that VC of size at most k might or might not exist,

function_to_be_applied : a function that has to be applied after finding a vertex cover for the reduced instance
    The signature of this function is same throughout
        Parameters
        ---------
            is_k_vc_exists : bool,
                                which is True if and only if the 
                                reduced instance g_new has a vertex cover of size at most k_new
            vc :
                vertex cover of the reduced instance (g_new, k_new)
"""


@not_implemented_for("directed")
def _remove_isolated_vertices(G, k, vc):
    applied = False
    k_new = k
    g_new = G

    is_k_vc_possible = True

    if k <= 0:
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    isolated_vertices = list(isolates(G))
    if isolated_vertices:
        g_new.remove_nodes_from(isolated_vertices)
        applied = True

    def function_to_be_applied_after_isolated_vertices(is_k_vc_exists, vc):
        if not is_k_vc_exists:
            return
        # no need to add isolated vertices
        return

    return (
        applied,
        g_new,
        k_new,
        is_k_vc_possible,
        function_to_be_applied_after_isolated_vertices,
    )


@not_implemented_for("directed")
def _remove_self_loops(G, k, vc):
    applied = False
    k_new = k
    g_new = G
    is_k_vc_possible = True
    self_loop_node = None

    for node, neighbour_dictionary in g_new.adjacency():
        if node in neighbour_dictionary:
            self_loop_node = node
            break

    if self_loop_node is None:
        return (applied, g_new, k_new, is_k_vc_possible, None)

    if k <= 0:
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )
    g_new.remove_node(self_loop_node)
    k_new = k - 1
    applied = True

    def function_to_be_applied_after_self_loops(is_k_vc_exists, vc):
        if not is_k_vc_exists:
            return
        vc.update([self_loop_node])

    return (
        applied,
        g_new,
        k_new,
        is_k_vc_possible,
        function_to_be_applied_after_self_loops,
    )


@not_implemented_for("directed")
def _deg_one_preprocessing(G, k, vc):
    applied = False
    k_new = k
    g_new = G
    is_k_vc_possible = True

    node = None
    for u in G:
        if G.degree(u) == 1:
            node = u
            break

    if node is None:
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    if k <= 0:
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    # if there is a degree one vertex, add its neigbour to vertex cover
    # and remove the neighbour from the graph
    # thereby reducing the size of the graph
    neighbour = list(g_new.neighbors(node))[0]

    g_new.remove_nodes_from([node, neighbour])
    k_new = k - 1

    applied = True

    def function_to_be_applied_after_deg_one(is_k_vc_exists, vc):
        if not is_k_vc_exists:
            return

        vc.update([neighbour])

    return (
        applied,
        g_new,
        k_new,
        is_k_vc_possible,
        function_to_be_applied_after_deg_one,
    )


@not_implemented_for("directed")
def _deg_two_preprocessing(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    is_k_vc_possible = True
    node = None

    for u in g_new:
        if g_new.degree(u) == 2:
            node = u
            break

    if node is None:
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    if k <= 0:
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    # neighbours of degree 2 vertices
    # x and y will not be the same since, already preprocessing self loop nodes
    x, y = tuple(g_new.neighbors(node))

    if g_new.has_edge(x, y):
        # k has to be atleast 2
        if k <= 1:
            is_k_vc_possible = False
            return (
                applied,
                g_new,
                k_new,
                is_k_vc_possible,
                None,
            )

        # add x and y to the solution reduce the graph instance
        g_new.remove_nodes_from([x, y, node])
        k_new = k - 2
        applied = True

        def function_to_be_applied_deg_two_first_case(is_k_vc_exists, vc):
            if not is_k_vc_exists:
                return

            vc.update([x, y])

        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            function_to_be_applied_deg_two_first_case,
        )

    else:
        # x, y are not adjacent
        # del node, x, y and add new vertex z adjacent to N(x) union N(y) - node
        # recurse on G', k - 1

        g_new.remove_node(node)
        # identify x and y
        # identified node is generally the first argument
        g_new = nx.identified_nodes(g_new, x, y, copy=False)
        k_new = k - 1
        applied = True

        def function_to_be_applied_deg_two_second_case(is_k_vc_exists, vc):
            if not is_k_vc_exists:
                return

            if x in vc:
                # remove identified vertex and add the original 2 vertex
                vc.update([x, y])

            else:
                vc.update([node])

        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            function_to_be_applied_deg_two_second_case,
        )


@not_implemented_for("directed")
def _high_degree_vertex_preprocessing(G, k, vc):
    """
    If there exists a vertex of degree > k, then any vertex cover of G of size at most k,
    must contain that vertex
    """
    applied = False
    g_new = G
    k_new = k
    is_k_vc_possible = True

    node = None
    for u in G:
        if G.degree(u) >= k + 1:
            # any vertex cover of size atmost k must contain u
            node = u
            break

    if node is None:
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    if k <= 0:
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    g_new.remove_node(node)
    k_new = k - 1
    applied = True

    def function_to_be_applied_after_high_degree(is_k_vc_exists, vc):
        if not is_k_vc_exists:
            return
        vc.update([node])

    return (
        applied,
        g_new,
        k_new,
        is_k_vc_possible,
        function_to_be_applied_after_high_degree,
    )


@not_implemented_for("directed")
def _check_bipartite_graph(G, k, vc):
    applied = False
    g_new = G
    k_new = k
    is_k_vc_possible = True

    if not nx.is_bipartite(g_new) or len(g_new) == 0:
        # empty graph is also recognised as bipartite, for which we don't want to apply preprocessing rule
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    coloring = nx.bipartite.color(g_new)
    top_nodes = [key for key, val in coloring.items() if val == 0]

    maximum_matching = hopcroft_karp_matching(g_new, top_nodes=top_nodes)
    min_vertex_cover = to_vertex_cover(g_new, maximum_matching, top_nodes=top_nodes)

    if k < len(min_vertex_cover):
        is_k_vc_possible = False
        return (
            applied,
            g_new,
            k_new,
            is_k_vc_possible,
            None,
        )

    # if graph is bipartite, then find min vertex cover in poly time
    # and clear the graph
    g_new.clear()
    k_new = k - len(min_vertex_cover)
    applied = True

    def function_to_be_applied_after_bipartite(is_k_vc_exists, vc):
        if not is_k_vc_exists:
            return

        vc.update(min_vertex_cover)

    return (
        applied,
        g_new,
        k_new,
        is_k_vc_possible,
        function_to_be_applied_after_bipartite,
    )


# @not_implemented_for("directed")
# def _crown_decomposition_based_preprocessing(G, k, vc):
#     """
#     If the graph has crown decomposition (C, H, R), we can reduce the instance to
#     (G - (H union C), k - |H|)
#
#     Reference
#     --------
#     .. [1] Section 2.3 and Section 2.3.1 in
#     [Marek Cygan, Fedor V. Fomin, Lukasz Kowalik, Daniel Lokshtanov, Daniel Marx, Marcin Pilipczuk, Michal Pilipczuk, and Saket Saurabh. 2015. Parameterized Algorithms (1st. ed.). Springer Publishing Company, Incorporated.](https://doi.org/10.1007/978-3-319-21275-3)
#
#     """
#     applied = False
#     g_new = G
#     k_new = k
#     is_k_vc_possible = True
#
#     # need to check if this is ok
#     if k <= 0 or len(G) <= 3 * k:
#         # print("GRAPH SIZE ATMOST 3 * k")
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     head_vertices, crown, rest, is_k_vc_possible = _crown_decomposition(g_new, k_new)
#     if not is_k_vc_possible:
#         # print("VC NOT POSSIBLE")
#         is_k_vc_possible = False
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     head_union_crown = head_vertices.union(crown)
#     if k < len(head_vertices):
#         # print("VC NOT POSSIBLE, size of head union crown exceeding k")
#         is_k_vc_possible = False
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#     if len(head_union_crown) == 0:
#         # is this check necessary ?
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     g_new.remove_nodes_from(head_union_crown)
#     k_new = k - len(head_vertices)
#     applied = True
#
#     def function_to_be_applied_after_crown_decomposition(is_k_vc_exists, vc):
#         if not is_k_vc_exists:
#             return
#
#         vc.update(head_vertices)
#
#     return (
#         applied,
#         g_new,
#         k_new,
#         is_k_vc_possible,
#         function_to_be_applied_after_crown_decomposition,
#     )
#
#
# @not_implemented_for("directed")
# def _lp_decomposition_based_preprocessing(G, k, vc):
#     """
#     Reference
#     ---------
#     .. [1] Section 3.4
#     [Marek Cygan, Fedor V. Fomin, Lukasz Kowalik, Daniel Lokshtanov, Daniel Marx, Marcin Pilipczuk, Michal Pilipczuk, and Saket Saurabh. 2015. Parameterized Algorithms (1st. ed.). Springer Publishing Company, Incorporated.](https://doi.org/10.1007/978-3-319-21275-3)
#
#     """
#     applied = False
#     g_new = G
#     k_new = k
#     is_k_vc_possible = True
#
#     # need to check if this is ok
#     if k <= 0 or len(G) <= 2 * k:
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     lp_value, greater_than_half, less_than_half, equal_to_half = _lp_decomposition_vc(
#         G, k
#     )
#
#     if lp_value > k:
#         # if lp_value is greater than k, then no vc of size atmost k exists
#         is_k_vc_possible = False
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     if len(equal_to_half) == len(G):
#         # then all halfs is the unique optimum
#         # then set applied as False and return from this preprocessing rule
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     else:
#         # we can add greater_than_half set to the vertex cover
#         # and remove union of greater_than_half and less_than_half from the graph
#         if len(greater_than_half) > k:
#             # then k vc is not possible
#             is_k_vc_possible = False
#             return (
#                 applied,
#                 g_new,
#                 k_new,
#                 is_k_vc_possible,
#                 None,
#             )
#
#         g_new.remove_nodes_from(greater_than_half.union(less_than_half))
#         k_new = k - len(greater_than_half)
#         applied = True
#
#         def function_to_be_applied_after_lp_all_half_not_unique_optimum(
#             is_k_vc_exists, vc
#         ):
#             if not is_k_vc_exists:
#                 return
#             vc.update(greater_than_half)
#
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             function_to_be_applied_after_lp_all_half_not_unique_optimum,
#         )
#
#
# @not_implemented_for("directed")
# def _surplus_one_neighbours_not_independent(G, k, vc):
#     """
#     Reference
#     ---------
#     .. [1] [Faster Parameterized Algorithms using Linear Programming](https://arxiv.org/abs/1203.0833)
#
#     """
#     applied = False
#     g_new = G
#     k_new = k
#     is_k_vc_possible = True
#
#     # print(G.edges(), k, vc)
#
#     if k <= 0 or len(G) == 0:
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     # if there is an edge (u, v) such that solving LPVC(G) with x(u) = x(v) = 1
#     # results in a solution with value exactly half greater than the value of the original LPVC(G)
#
#     # since at this point all halfs would be the solution
#     original_lp_value = len(G) / 2
#
#     for u, v in G.edges:
#         lp_value_new, g_half, l_half, e_half = _partial_weighted_lp_decomposition(
#             G, {u: 1, v: 1}
#         )
#         if lp_value_new == original_lp_value + 0.5:
#             # set with surplus one is l_half set
#             Z = l_half
#             N_Z = set()
#
#             for u in Z:
#                 N_Z.update(G.neighbors(u))
#
#             N_Z.difference_update(Z)
#
#             # we can add N_Z to the vertex cover
#             # delete Z union N_Z from the graph and decrease k by |N_Z|
#             if k < len(N_Z):
#                 is_k_vc_possible = False
#                 return (
#                     applied,
#                     g_new,
#                     k_new,
#                     is_k_vc_possible,
#                     None,
#                 )
#
#             g_new.remove_nodes_from(Z.union(N_Z))
#             k_new = k - len(N_Z)
#             applied = True
#
#             def function_to_be_applied_after_surplus_one_neighbours_not_independent_set(
#                 is_k_vc_exists, vc
#             ):
#                 if not is_k_vc_exists:
#                     return
#                 # print(f"Neighbourign set is {N_Z}")
#                 vc.update(N_Z)
#
#             return (
#                 applied,
#                 g_new,
#                 k_new,
#                 is_k_vc_possible,
#                 function_to_be_applied_after_surplus_one_neighbours_not_independent_set,
#             )
#
#     return (
#         applied,
#         g_new,
#         k_new,
#         is_k_vc_possible,
#         None,
#     )
#
#
# @not_implemented_for("directed")
# def _surplus_one_neighbours_independent(G, k, vc):
#     """
#     Reference
#     ---------
#     .. [1] [Faster Parameterized Algorithms using Linear Programming](https://arxiv.org/abs/1203.0833)
#
#     """
#     applied = False
#     g_new = G
#     k_new = k
#     is_k_vc_possible = True
#
#     if k <= 0 or len(G) == 0:
#         return (
#             applied,
#             g_new,
#             k_new,
#             is_k_vc_possible,
#             None,
#         )
#
#     # if there is a vertex such that solving LPVC(G) with x(u) = 0 results in a solution with value
#     # exactly 0.5 greater than the value of original LPVC(G)
#
#     # since at this point all halfs would be the solution
#     original_lp_value = len(G) / 2
#
#     for u in G:
#         lp_value_new, g_half, l_half, e_half = _partial_weighted_lp_decomposition(
#             G, {u: 0}
#         )
#         if lp_value_new == original_lp_value + 0.5:
#             # then Z is the l_half set
#             # and G has a VC of size atmost k if and only ???
#
#             # set with surplus one is l_half set
#             Z = l_half
#             N_Z = set()
#
#             for u in Z:
#                 N_Z.update(G.neighbors(u))
#
#             N_Z.difference_update(Z)
#
#             if k < len(Z):
#                 is_k_vc_possible = False
#                 return (
#                     applied,
#                     g_new,
#                     k_new,
#                     is_k_vc_possible,
#                     None,
#                 )
#
#             # remove Z and N_Z from graph and identify N_Z by single vertex
#             N_Z_list = list(N_Z)
#             g_new.remove_nodes_from(Z)
#
#             # N_Z is independent, hence contracting N_Z doesn't produce self loops
#             node = N_Z_list[0]
#             for i in range(1, len(N_Z_list)):
#                 g_new = nx.identified_nodes(g_new, node, N_Z_list[i], copy=False)
#
#             k_new = k - len(Z)
#             applied = True
#
#             # `node` is the identified vertex
#             def function_to_be_applied_after_surplus_one_neighbours_independent_set(
#                 is_k_vc_exists, vc
#             ):
#                 if not is_k_vc_exists:
#                     return
#
#                 if node in vc:
#                     vc.update(N_Z)
#                 else:
#                     vc.update(Z)
#
#             return (
#                 applied,
#                 g_new,
#                 k_new,
#                 is_k_vc_possible,
#                 function_to_be_applied_after_surplus_one_neighbours_independent_set,
#             )
#
#     return (applied, g_new, k_new, is_k_vc_possible, None)
