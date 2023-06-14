"""Time dependent algorithms."""

from datetime import datetime

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["cd_index"]


@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def cd_index(G, node, time_delta=5, weight=None):
    r"""Compute the CD index for `node` within the graph `G`.

    Calculates the CD index for the given node of the graph,
    considering only its predecessors who have `time` attribute
    smaller than or equal to the `time` attribute of the `node`
    plus `time_delta` years.

    Parameters
    ----------
    G : graph
       A directed networkx graph whose nodes have datetime `time` attributes and
       optionally `weight` attributes (if a weight is not given, it is considered 1).
    node : node
       The node for which the CD index is calculated.
    time_delta : integer (Optional, default is 5)
       Number of years after the `time` attribute of the `node`.

    Returns
    -------
    float
       The CD index calculated for the node `node` within the graph `G`.

    Raises
    ------
    ValueError
       If not all nodes have a datetime `time` attribute or
       `n' equals 0.

    NetworkXNotImplemented
        If `G` is a non-directed graph or a multigraph.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nodes = { 1: {'time': datetime(2015, 1, 1)}, \
    ...     2: {'time': datetime(2012, 1, 1), 'weight': 4}, \
    ...     3: {'time': datetime(2010, 1, 1)}, \
    ...     4: {'time': datetime(2008, 1, 1)}, \
    ...     5: {'time': datetime(2014, 1, 1)}}
    >>> G.add_nodes_from([(n, nodes[n]) for n in nodes])
    >>> edges = [(1, 3), (1, 4), (2, 3), (3, 4), (3, 5)]
    >>> G.add_edges_from(edges)
    >>> cd = nx.cd_index(G, 3, weight="weight")

    Notes
    -----
    This method implements the algorithm for calculating the CD index,
    as described in the paper by Funk and Owen-Smith [1]. The CD index
    is used in order to check how consolidating or destabilizing a patent
    is, hence the nodes of the graph represent patents and the edges show
    the citations between these patents. The mathematical model is given
    below: 

    .. math::
        CD_{t}=\frac{1}{n_{t}}\sum_{i=1}^{n}\frac{-2f_{it}b_{it}+f_{it}}{w_{it}},

    where `f_{it}` equals 1 if `i` cites the focal patent else 0, `b_{it}` equals
    1 if `i` cites any of the focal patents successors else 0, `n_{t}` is the number
    of forward citations in `i` and `w_{it}` is a matrix of weight for patent `i`
    at time `t`.

    References
    ----------
    .. [1] Funk, Russell J., and Jason Owen-Smith.
           "A dynamic network measure of technological change."
           Management science 63, no. 3 (2017): 791-817.
           http://russellfunk.org/cdindex/static/papers/funk_ms_2017.pdf

    """
    if not all(isinstance(G.nodes[n].get("time"), datetime) for n in G):
        raise ValueError("Not all nodes have a datetime 'time' attribute.")

    # get target_date's unix timestamp
    target_date = G.nodes[node]["time"].timestamp() + time_delta * 365 * 24 * 60 * 60

    # keep the predecessors that existed before the target date
    pred = {i for i in G.pred[node] if G.nodes[i]["time"].timestamp() <= target_date}

    # -1 if any edge between node's predecessors and node's successors, else 1
    b = [-1 if any(j in G[i] for j in G[node]) else 1 for i in pred]

    # n is size of the union of the focal node's predecessors and its successors' predecessors
    n = len(pred.union(*(G.pred[s].keys() - {node} for s in G[node])))
    if n == 0:
        raise ValueError("The cd index cannot be defined.")

    # calculate cd index
    if weight is None:
        return round(sum(bi for bi in b) / n, 2)
    else:
        # If a node has the specified weight attribute, its weight is used in the calculation
        # otherwise, a weight of 1 is assumed for that node
        weights = [G.nodes[i].get(weight, 1) for i in pred]
        return round(sum(bi / wt for bi, wt in zip(b, weights)) / n, 2)
