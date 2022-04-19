"""Degree centrality measures."""
from networkx.utils.decorators import not_implemented_for

__all__ = ["degree_centrality", "in_degree_centrality", "out_degree_centrality"]


def degree_centrality(G):
    """Compute the degree centrality for nodes.

       The degree centrality for a node v is the fraction of nodes it
       is connected to.

       Parameters
       ----------
       G : graph
         A networkx graph

       Returns
       -------
       nodes : dictionary
          Dictionary of nodes with degree centrality as the value.

       Examples
       --------
       >>> G = nx.Graph([(0, 1), (1, 2), (1, 5), (5, 4), (2, 4), (2, 3), (4, 3)])
       >>> nx.degree_centrality(G)
       {0: 0.2,
    1: 0.6000000000000001,
    2: 0.6000000000000001,
    5: 0.4,
    4: 0.6000000000000001,
    3: 0.4}

       See Also
       --------
       betweenness_centrality, load_centrality, eigenvector_centrality

       Notes
       -----
       The degree centrality values are normalized by dividing by the maximum
       possible degree in a simple graph n-1 where n is the number of nodes in G.

       For multigraphs or graphs with self loops the maximum degree might
       be higher than n-1 and values of degree centrality greater than 1
       are possible.
    """
    if len(G) <= 1:
        return {n: 1 for n in G}

    s = 1.0 / (len(G) - 1.0)
    centrality = {n: d * s for n, d in G.degree()}
    return centrality


@not_implemented_for("undirected")
def in_degree_centrality(G):
    """Compute the in-degree centrality for nodes.

    The in-degree centrality for a node v is the fraction of nodes its
    incoming edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with in-degree centrality as values.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Examples
       --------
       >>> G = nx.Graph([(0, 1), (1, 2), (1, 5), (5, 4), (2, 4), (2, 3), (4, 3)])
       >>> nx.in_degree_centrality(G)
       {0: 0.0, 1: 0.2, 2: 0.2, 5: 0.2, 4: 0.4, 3: 0.4}

    See Also
    --------
    degree_centrality, out_degree_centrality

    Notes
    -----
    The degree centrality values are normalized by dividing by the maximum
    possible degree in a simple graph n-1 where n is the number of nodes in G.

    For multigraphs or graphs with self loops the maximum degree might
    be higher than n-1 and values of degree centrality greater than 1
    are possible.
    """
    if len(G) <= 1:
        return {n: 1 for n in G}

    s = 1.0 / (len(G) - 1.0)
    centrality = {n: d * s for n, d in G.in_degree()}
    return centrality


@not_implemented_for("undirected")
def out_degree_centrality(G):
    """Compute the out-degree centrality for nodes.

    The out-degree centrality for a node v is the fraction of nodes its
    outgoing edges are connected to.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    Returns
    -------
    nodes : dictionary
        Dictionary of nodes with out-degree centrality as values.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Examples
       --------
       >>> G = nx.Graph([(0, 1), (1, 2), (1, 5), (5, 4), (2, 4), (2, 3), (4, 3)])
       >>> nx.out_degree_centrality(G)
       {0: 0.2, 1: 0.4, 2: 0.4, 5: 0.2, 4: 0.2, 3: 0.0}

    See Also
    --------
    degree_centrality, in_degree_centrality

    Notes
    -----
    The degree centrality values are normalized by dividing by the maximum
    possible degree in a simple graph n-1 where n is the number of nodes in G.

    For multigraphs or graphs with self loops the maximum degree might
    be higher than n-1 and values of degree centrality greater than 1
    are possible.
    """
    if len(G) <= 1:
        return {n: 1 for n in G}

    s = 1.0 / (len(G) - 1.0)
    centrality = {n: d * s for n, d in G.out_degree()}
    return centrality
