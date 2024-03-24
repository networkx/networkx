"""
Implements the calculation of a Randic index for a graph._summary_
"""
import networkx as nx

from math import sqrt
from networkx.utils import not_implemented_for

__all__ = ["randic_index"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def randic_index(G):
    r"""
    Compute the Randic index of the graph.

    Parameters
    ----------
    G : graph
        A Networkx graph.

    Returns
    -------
    index: int
        The calculated Randic Index of the graph.


    Raises
    ------
    NetowrkXNotImplemented
        The algorithm does not support DiGraph, MultiGraph, and MultiDiGraph

    Examples
    --------
    >>> g = nx.complete_graph(5)
    >>> randic_index(g)
    2.5

    Notes
    -----
    The Randic index [1] is a theoretical characterization of molecular branching, where
    the molecules can be represented as undirected graphs. The Randic index is calculated as:
    $R(G) = \sum_{u,v \in E} (deg(u)deg(v))^{-1/2}$.

    References
    --------
        [1] Randic, M. (1975). Characterization of molecular branching.
        Journal of the American Chemical Society, 97(23), 6609-6615.
    """

    index = sum((1 / sqrt(G.degree(u) * G.degree(v))) for u, v in G.edges())
    return index
