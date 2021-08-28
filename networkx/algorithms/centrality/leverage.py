"""Functions for computing eigenvector centrality."""

from math import sqrt
import networkx as nx
from networkx.utils import not_implemented_for
import random

__all__ = ["leverage_centrality"]


@not_implemented_for("multigraph")
@not_implemented_for("directed")
def leverage_centrality(G, weight=None):
    """Compute the leverage centrality for the graph `G`.

    The definition has

    Leverage centrality considers the degree of a node relative to its neighbors and operates
    under the principle that a node in a network is central if its immediate neighbors rely on
    that node for information.

    Leverage centrality is a measure of the relationship between the degree of a given node($k_{i}$)
    and the degree of each of its neighbors ($k_{j}$), averaged over all neighbors ($N_{i}$),
    and is defined as shown below.

    .. math::
       LC_{i}   = \frac{1}{k_{i}} \sum_{N_{j}} \frac{k_{i} - k_{j}}{k_{i} + k_{j}}

    A node with negative leverage centrality is influenced by its neighbors, as the neighbors connect
    and interact with far more nodes. A node with positive leverage centrality, on the other hand,
    influences its neighbors since the neighbors tend to have far fewer connections.

    Parameters
    ----------
    G : graph
    A networkx graph

    weight : None or string, optional (default=None)
    If None, all edge weights are considered equal.
    Otherwise holds the name of the edge attribute used as weight.
    In this measure the weight is interpreted as the connection strength.

    Returns
    -------
    nodes : dictionary
    Dictionary of nodes with leverage centrality as the value.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> leverage_cent = nx.leverage_centrality(G)
    >>> sorted((v, f"{c:0.2f}") for v, c in leverage_cent.items())
    [(0, '-0.33'), (1, '0.17'), (2, '0.17'), (3, '-0.33')]

    Raises
    ------
    NetworkXPointlessConcept
    If the graph `G` is the null graph.

    See Also
    --------
    eigenvector_centrality
    degree_centrality
    pagerank

    Notes
    -----
    1. Leverage Centrality is undefined for nodes with degree = 0.
    2. The implementation has not been designed for use with directed graphs and multigraphs.

    References
    ----------
    [1] Joyce, Karen E., Paul J. Laurienti, Jonathan H. Burdette, and Satoru Hayasaka.
    "A new measure of centrality for brain networks." PloS one 5.8 (2010): e12200.
    https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0012200
    [2] https://www.centiserver.org/centrality/Leverage_Centrality/
    """
    # If the initial graph has no nodes
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "cannot compute centrality for the null graph"
        )

    # leverage centrality dictionary
    leverage_cent = {}
    # Computing Degrees, wieghted or unweighted
    degrees = G.degree(weight=weight)
    # Iterating over all the nodes
    for n in G.nodes():
        # Initial leverage centrality
        LCsum_n = 0
        degree_n = degrees[n]
        # Leverage centrality is undefined for a node with degree 0
        if degree_n == 0:
            raise nx.NetworkXPointlessConcept(
                "cannot compute centrality for a node with no degree = 0", n
            )
        # Getting all the neighbors of the node n
        neighbors = G.neighbors(n)
        # Iterating through all the neighbors and getting their 'share' from the algo
        for neighbor in neighbors:
            degree_neighbor = degrees[neighbor]
            LCsum_n += (degree_n - degree_neighbor) / (degree_n + degree_neighbor)
        # Normalizing by the degree of the node
        LCsum_n /= degree_n
        # Storing in the dictionary
        leverage_cent[n] = LCsum_n
    return leverage_cent
