from warnings import warn

from graphblas import Vector, binary, unary
from graphblas.semiring import plus_first, plus_times
from graphblas_algorithms.algorithms.link_analysis.pagerank_alg import \
    pagerank_core
from graphblas_algorithms.classes.digraph import to_graph

import networkx as nx


def pagerank(
    G,
    alpha=0.85,
    personalization=None,
    max_iter=100,
    tol=1e-06,
    nstart=None,
    weight="weight",
    dangling=None,
):
    G = to_graph(G, weight=weight, dtype=float)
    N = len(G)
    if N == 0:
        return {}
    # We'll normalize initial, personalization, and dangling vectors later
    x = G.dict_to_vector(nstart, dtype=float, name="nstart")
    p = G.dict_to_vector(personalization, dtype=float, name="personalization")
    row_degrees = G.get_property("plus_rowwise+")  # XXX: What about self-edges?
    if dangling is not None and row_degrees.nvals < N:
        dangling_weights = G.dict_to_vector(dangling, dtype=float, name="dangling")
    else:
        dangling_weights = None
    result = pagerank_core(
        G,
        alpha=alpha,
        personalization=p,
        max_iter=max_iter,
        tol=tol,
        nstart=x,
        dangling=dangling_weights,
        row_degrees=row_degrees,
    )
    return G.vector_to_dict(result, fillvalue=0.0)
