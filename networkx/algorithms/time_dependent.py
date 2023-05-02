"""Time dependent algorithms."""

from datetime import datetime

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["cd_index"]


@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def cd_index(G, node, time_delta=5):
    """Compute the CD index.

    Calculates the CD index for the graph based on the given "focal patent" node
    considering the patents after time_delta years.

    Parameters
    ----------
    G : graph
       A directed networkx graph whose nodes have datetime 'time' attributes.
    node : integer
       Focal node that represents the focal patent.
    time_delta : integer
       Number of years after creation of focal patent.

    Returns
    -------
    float
       The CD index calculated for the G graph.

    Examples
    --------

    Notes
    -----


    """
    if not (
        all(
            G.has_node(n)
            and "time" in G.nodes[n]
            and isinstance(G.nodes[n]["time"], datetime)
            for n in G
        )
    ):
        raise ValueError("Not all nodes have a datetime 'time' attribute.")

    target_date = G.nodes[node]["time"].timestamp() + time_delta * 365 * 24 * 60 * 60
    succ, pred = list(G.successors(node)), list(G.predecessors(node))

    if not succ:
        raise ValueError("This node has no successors.")

    actual_pred = [i for i in pred if G.nodes[i]["time"].timestamp() <= target_date]

    if not actual_pred:
        raise ValueError("This node has no predecessors.")

    b = [int(any((i, j) in G.edges() for j in succ)) for i in actual_pred]
    n = set(actual_pred)
    for s in succ:
        n |= set(G.predecessors(s)) - {node}

    return round(sum((-2) * bi + 1 for bi in b) / len(n), 2)
