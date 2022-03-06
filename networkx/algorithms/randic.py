"""
Implements the calculation of a Rancic index for a graph._summary_
"""
import networkx as nx
import numpy as np
from networkx.utils import not_implemented_for

__all__ = ["randic_index"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def randic_index(G):
    """Compute the Randic index of the graph.

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
    ***Notes regarding bounds of Randic index go here***

    See Also
    --------

    """
    # TODO: add edge weights to graph?
    #      Return graph with edges or just randic index?
    #      Is there a way to store the randic index in the graph?

    deg_dict = G.degree(G.nodes)
    index = np.sum(
        [(1 / np.sqrt(deg_dict[edge[0]] * deg_dict[edge[1]])) for edge in G.edges]
    )

    return index
