# import networkx as nx
# from networkx.algorithms.bipartite import hopcroft_karp_matching
# from networkx.algorithms.bipartite.matching import to_vertex_cover
# from networkx.utils import not_implemented_for
#
# __all__ = ["_crown_decomposition"]
#
#
# @not_implemented_for("directed")
# def _crown_decomposition(G, k):
#     """
#     Given a graph `G` and a parameter `k`,
#     returns
#     H, C, R, is_k_vc_possible where (C, H, R) denotes a crown decomposition of graph G,
#     if one exists, and if a matching of size more than k is found, then is_k_vc_possible = False
#     and C = H = R = empty set
#     """
#
#     # it should be ensured in this algorithm that, k does not become negative
#     aux_bipartite_graph = G.copy()
#     is_k_vc_possible = True
#     head_vertices = set()
#     crown = set()
#     rest = set()
#
#     maximal_matching = nx.maximal_matching(aux_bipartite_graph)
#     if len(maximal_matching) > k:
#         is_k_vc_possible = False
#         return head_vertices, crown, rest, is_k_vc_possible
#
#     v_from_maximal_matching = set()
#     for a, b in maximal_matching:
#         v_from_maximal_matching.add(a)
#         v_from_maximal_matching.add(b)
#
#     # v_from_maximal_matching consists of the nodes in one side of the new auxiliary bi partite graphs
#     graph_nodes = set(aux_bipartite_graph.nodes)
#
#     for node in v_from_maximal_matching:
#         neighbors = list(aux_bipartite_graph.neighbors(node))
#         for neighbor in neighbors:
#             if neighbor in v_from_maximal_matching:
#                 # the loop takes each vertetx from the set of vertices
#                 # in v_from_maximal_matching and deletes the edges present
#                 # between this vertex and all vertices
#                 # present in v_from_maximal_matching
#                 aux_bipartite_graph.remove_edge(node, neighbor)
#
#     # now we need to find a maximum matching and a minimum vertex cover of the new graph
#
#     # applying hopcraft karp algorithm
#     maximum_matching = hopcroft_karp_matching(
#         aux_bipartite_graph,
#         top_nodes=v_from_maximal_matching,
#     )
#
#     if len(maximum_matching) > k:
#         is_k_vc_possible = False
#         return head_vertices, crown, rest, is_k_vc_possible
#
#     minimum_vertex_cover = to_vertex_cover(
#         aux_bipartite_graph, maximum_matching, top_nodes=v_from_maximal_matching
#     )
#
#     # this returns a set of minimm vertex cover in this new auxiliary graph
#
#     head_vertices = v_from_maximal_matching.intersection(minimum_vertex_cover)
#     # crown is the matching partners of vertices in head_vertices
#     crown.add([maximum_matching[a] for a in head_vertices])
#
#     # assert len(crown) != 0, "Crown Size is zero"
#
#     rest = graph_nodes.difference(head_vertices.union(crown))
#
#     return head_vertices, crown, rest, is_k_vc_possible
