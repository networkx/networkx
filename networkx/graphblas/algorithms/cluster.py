from graphblas import binary
from graphblas.semiring import plus_pair
from graphblas_algorithms.algorithms.cluster import (
    average_clustering_core, average_clustering_directed_core, clustering_core,
    clustering_directed_core, single_clustering_core,
    single_clustering_directed_core, single_triangle_core, transitivity_core,
    transitivity_directed_core, triangles_core)
from graphblas_algorithms.classes.digraph import to_graph
from graphblas_algorithms.classes.graph import to_undirected_graph
from graphblas_algorithms.utils import not_implemented_for

from networkx import average_clustering as _nx_average_clustering
from networkx import clustering as _nx_clustering


@not_implemented_for("directed")
def triangles(G, nodes=None):
    G = to_undirected_graph(G, dtype=bool)
    if len(G) == 0:
        return {}
    if nodes in G:
        return single_triangle_core(G, nodes)
    mask = G.list_to_mask(nodes)
    result = triangles_core(G, mask=mask)
    return G.vector_to_dict(result, mask=mask, fillvalue=0)


def average_clustering(G, nodes=None, weight=None, count_zeros=True):
    if weight is not None:
        # TODO: Not yet implemented.  Clustering implemented only for unweighted.
        return _nx_average_clustering(
            G, nodes=nodes, weight=weight, count_zeros=count_zeros
        )
    G = to_graph(G, weight=weight)  # to directed or undirected
    if len(G) == 0:
        raise ZeroDivisionError()  # Not covered
    mask = G.list_to_mask(nodes)
    if G.is_directed():
        func = average_clustering_directed_core
    else:
        func = average_clustering_core
    if mask is None:
        return G._cacheit(
            f"average_clustering(count_zeros={count_zeros})",
            func,
            G,
            count_zeros=count_zeros,
        )
    else:
        return func(G, mask=mask, count_zeros=count_zeros)


def clustering(G, nodes=None, weight=None):
    if weight is not None:
        # TODO: Not yet implemented.  Clustering implemented only for unweighted.
        return _nx_clustering(G, nodes=nodes, weight=weight)
    G = to_graph(G, weight=weight)  # to directed or undirected
    if len(G) == 0:
        return {}
    if nodes in G:
        if G.is_directed():
            return single_clustering_directed_core(G, nodes)
        else:
            return single_clustering_core(G, nodes)
    mask = G.list_to_mask(nodes)
    if G.is_directed():
        result = clustering_directed_core(G, mask=mask)
    else:
        result = clustering_core(G, mask=mask)
    return G.vector_to_dict(result, mask=mask, fillvalue=0.0)


def transitivity(G):
    G = to_graph(G, dtype=bool)  # directed or undirected
    if len(G) == 0:
        return 0
    if G.is_directed():
        func = transitivity_directed_core
    else:
        func = transitivity_core
    return G._cacheit("transitivity", func, G)
