"""Time dependent algorithms."""

from datetime import datetime

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["cd_index"]


@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def cd_index(G, node, time_delta=5, weight=None):
    r"""Compute the CD index.

    Calculates the CD index for the graph based on the given "focal patent" node
    considering the patents after `time_delta` years.

    Parameters
    ----------
    G : graph
       A directed networkx graph whose nodes have datetime `time` attributes.
    node : integer
       Focal node that represents the focal patent.
    time_delta : integer (Optional, default is 5)
       Number of years after creation of focal patent.
    weight : list of floats (Optional)
       A list of weights for focal patent's predecessors `time_delta` years after its creation.

    Returns
    -------
    float
       The CD index calculated for the G graph.

    Raises
    ------
    ValueError
       If not all nodes have a datetime `time` attribute or
       `node` has no successors or
       `node` has no predecessors.

    NetworkXNotImplemented
        If `G` is a non-directed graph or a multigraph.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nodes = {
    1: {'time': datetime(2015, 1, 1)},
    2: {'time': datetime(2012, 1, 1)},
    3: {'time': datetime(2010, 1, 1)},
    4: {'time': datetime(2008, 1, 1)},
    5: {'time': datetime(2014, 1, 1)}}
    >>> G.add_nodes_from([(n, nodes[n]) for n in nodes])
    >>> edges = [(1, 3), (1, 4), (2, 3), (3, 4), (3, 5)]
    >>> G.add_edges_from(edges)
    >>> cd = nx.cd_index(G, 3)

    Notes
    -----
    This method implements the algorithm for calculating the CD index,
    as described in the paper by Funk and Owen-Smith [1]:

    .. math::
        CD_{t}=\frac{1}{n_{t}}\sum_{i=1}^{n}\frac{-2f_{it}b_{it}+f_{it}}{w_{it}},

    where `f_{it}` equals 1 if `i` cites the focal patent else 0, `b_{it}` equals
    1 if `i` cites any of the focal patents accessors else 0, `n_{t}` is the number
    of forward citations in `i` and `w_{it}` is a matrix of weight for patent `i`
    at time `t`.

    References
    ----------
    .. [1] Funk, Russell J., and Jason Owen-Smith.
    "A dynamic network measure of technological change."
    Management science 63, no. 3 (2017): 791-817.
    http://russellfunk.org/cdindex/static/papers/funk_ms_2017.pdf

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

    # get target_date's unix timestamp
    target_date = G.nodes[node]["time"].timestamp() + time_delta * 365 * 24 * 60 * 60
    # get successors and predecessors of the focal node
    succ, pred = list(G.successors(node)), list(G.predecessors(node))

    if not succ:
        raise ValueError("This node has no successors.")

    # keep the predecessors that existed before the target date
    actual_pred = [i for i in pred if G.nodes[i]["time"].timestamp() <= target_date]

    if not actual_pred:
        raise ValueError("This node has no predecessors.")

    # 1 if any edge between a focal node's predecessor and a focal node's accessor
    # exists, else 0
    b = [int(any((i, j) in G.edges() for j in succ)) for i in actual_pred]
    n = set(actual_pred)

    # n is the union of the focal node's predecessors and its accessors' predecessors
    for s in succ:
        n |= set(G.predecessors(s)) - {node}

    # calculate cd index
    if weight is None:
        return round(sum((-2) * bi + 1 for bi in b) / len(n), 2)
    else:
        return round(
            sum((-2 * b[i] + 1) / weight[i] for i in range(len(b))) / len(n), 2
        )
