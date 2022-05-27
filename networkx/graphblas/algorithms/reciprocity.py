from graphblas import binary
from graphblas_algorithms.algorithms.reciprocity import (
    overall_reciprocity_core, reciprocity_core)
from graphblas_algorithms.classes.digraph import to_directed_graph

from networkx import NetworkXError
from networkx.utils import not_implemented_for


@not_implemented_for("undirected", "multigraph")
def reciprocity(G, nodes=None):
    if nodes is None:
        return overall_reciprocity(G)
    G = to_directed_graph(G, dtype=bool)
    if nodes in G:
        mask = G.list_to_mask([nodes])
        result = reciprocity_core(G, mask=mask)
        rv = result[G._key_to_id[nodes]].value
        if rv is None:
            raise NetworkXError("Not defined for isolated nodes.")
        else:
            return rv
    else:
        mask = G.list_to_mask(nodes)
        result = reciprocity_core(G, mask=mask)
        return G.vector_to_dict(result, mask=mask)


@not_implemented_for("undirected", "multigraph")
def overall_reciprocity(G):
    G = to_directed_graph(G, dtype=bool)
    return overall_reciprocity_core(G)
