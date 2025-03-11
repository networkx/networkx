import networkx as nx
from networkx.algorithms.tree.recognition import is_forest
from networkx.utils.decorators import not_implemented_for


@not_implemented_for("directed")
def is_fvs(G, fvs):
    """
    Checks if a given set `fvs` is a feedback vertex set of `G`
    """
    H = G.subgraph(set(G.nodes) - fvs)

    if len(H) == 0:
        return True

    return is_forest(G.subgraph(set(G.nodes) - fvs))
