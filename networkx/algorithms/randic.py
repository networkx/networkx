"""
Implements the calculation of a Rancic index for a graph._summary_
"""
import networkx as nx
from math import sqrt
from networkx.utils import not_implemented_for

__all__ = ["randic_index"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def randic_index(G):
    r"""Compute the Randic index of the graph.

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
    >>> G = nx.erdos_renyi_graph(n=50, p=0.5)
    >>> print(nx.randic_index(G))
    25

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

    deg_dict = G.degree(G.nodes)
    index = sum((1 / sqrt(deg_dict[edge[0]] * deg_dict[edge[1]])) for edge in G.edges)

    return index
