"""
Find the k-peaks of a graph.

See the following reference for details:

The k-peak Decomposition: Mapping the Global Structure of Graphs
Govindan Priya, Wang Chenghong, Xu Chumeng, Duan Hongyu, and Soundarajan Sucheta
WWW '17
https://doi.org/10.1145/3038912.3052635

"""

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for

__all__ = ["peak_number", "k_peak", "k_contour"]


@not_implemented_for("multigraph")
@nx._dispatch
def peak_number(G, cores=None):
    """Returns the peak number for each vertex.

    A k-peak of a graph is a maximal subgraph that contains nodes of degree k or more within each other.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph
    cores : dictionary, optional
      Precomputed core numbers for the graph G.

    Returns
    -------
    peak_number : dictionary
       A dictionary keyed by node to the peak number.

    Raises
    ------
    NetworkXError
        The k-peak is not implemented for graphs with self loops
        or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    See Also
    --------
    core_number

    References
    ----------
    .. [1] The k-peak Decomposition: Mapping the Global Structure of Graphs
    Govindan Priya, Wang Chenghong, Xu Chumeng, Duan Hongyu, and Soundarajan Sucheta
    WWW '17
    https://doi.org/10.1145/3038912.3052635

    """
    if nx.number_of_selfloops(G) > 0:
        msg = (
            "Input graph has self loops which is not permitted; "
            "Consider using G.remove_edges_from(nx.selfloop_edges(G))."
        )
        raise NetworkXError(msg)

    if cores is None:
        cores = nx.core_number(G)

    H = G.copy()
    peak_number = {}

    while H.nodes():
        core_degeneracy = nx.k_core(H, core_number=cores)
        peak_number.update({node: cores[node] for node in core_degeneracy})
        H.remove_nodes_from(core_degeneracy.nodes())
        cores = nx.core_number(H)

    return peak_number


@nx._dispatch(preserve_all_attrs=True)
def k_peak(G, k=None, cores=None, peaks=None):
    """Returns the k-peak of G.

    A k-peak of a graph is a maximal subgraph that contains nodes of degree k or more within each other.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph
    k : int, optional
      The order of the peak.  If not specified return the max peak.
    cores : dictionary, optional
      Precomputed core numbers for the graph G.
    peaks : dictionary, optional
      Precomputed peak numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-peak subgraph

    Raises
    ------
    NetworkXError
        The k-peak is not implemented for graphs with self loops
        or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number
    peak_number

    References
    ----------
    .. [1] The k-peak Decomposition: Mapping the Global Structure of Graphs
    Govindan Priya, Wang Chenghong, Xu Chumeng, Duan Hongyu, and Soundarajan Sucheta
    WWW '17
    https://doi.org/10.1145/3038912.3052635

    """
    if peaks is None:
        peaks = peak_number(G, cores=cores)

    if k is None:
        k = max(peaks.values())

    H = G.copy()
    H.remove_nodes_from([key for key, value in peaks.items() if value < k])

    return H


@nx._dispatch(preserve_all_attrs=True)
def k_contour(G, k=None, cores=None, peaks=None):
    """Returns the k-contour of G.

    A k-contour of a graph is a maximal subgraph that contains nodes of degree k within each other.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph
    k : int, optional
      The order of the peak.  If not specified return the max peak.
    cores : dictionary, optional
      Precomputed core numbers for the graph G.
    peaks : dictionary, optional
      Precomputed peak numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-contour subgraph

    Raises
    ------
    NetworkXError
        The k-contour is not implemented for graphs with self loops
        or parallel edges.

    Notes
    -----
    The k-contour does not include nodes with a higher or lower degree.

    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number
    peak_number
    k_peak

    References
    ----------
    .. [1] The k-peak Decomposition: Mapping the Global Structure of Graphs
    Govindan Priya, Wang Chenghong, Xu Chumeng, Duan Hongyu, and Soundarajan Sucheta
    WWW '17
    https://doi.org/10.1145/3038912.3052635

    """
    if peaks is None:
        peaks = peak_number(G, cores=cores)

    if k is None:
        k = max(peaks.values())

    H = G.copy()
    H.remove_nodes_from([key for key, value in peaks.items() if value != k])

    return H
