"""
Find the decompositions of a graph.

Two techniques are implemented: k-core and k-peak.

The highest possible k (for core or peak) is called degeneracy.

See the following references for details:

Graph core: https://networkx.org/documentation/stable/reference/algorithms/core.html

The k-peak Decomposition: Mapping the Global Structure of Graphs, Govindan Priya, Wang Chenghong, Xu Chumeng, Duan Hongyu, and Soundarajan Sucheta, WWW '17. https://doi.org/10.1145/3038912.3052635

"""

import networkx as nx

__all__ = [
    "k_core_decomposition",
    "k_core_degeneracy",
    "k_peak_decomposition",
    "k_peak_degeneracy",
]


@nx.utils.not_implemented_for("multigraph")
def k_core_decomposition(G, k, core_number=None):
    """Returns the k-core decomposition of G.

    The k-core decomposition is the subgraph of G that each node has `k` or more degree.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    k : int
      Value of the decomposition
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-core decomposition

    Raises
    ------
    NetworkXNotImplemented
      The k-core decomposition is not defined for multigraphs or graphs with self loops.

    See Also
    --------
    core_number

    """
    return nx.k_core(G, k=k, core_number=core_number)


@nx.utils.not_implemented_for("multigraph")
def k_core_degeneracy(G, core_number=None):
    """Returns the k-core degeneracy of G.

    The k-core degeneracy is the subgraph of G that each node has maximum core number degree.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-core degeneracy

    Raises
    ------
    NetworkXNotImplemented
      The k-core degeneracy is not defined for multigraphs or graphs with self loops.

    Notes
    -----
    K-core degeneracy is the highest k-core decomposition.

    See Also
    --------
    core_number
    k_core_decomposition

    """
    if core_number is None:
        core_number = nx.core_number(G)
    k = max(core_number.values())

    return nx.k_core(G, k=k, core_number=core_number)


def k_peak_decomposition(G, k, core_number=None, peak_number=None):
    """Returns the k-peak decomposition of G.

    The k-peak decomposition is the subgraph of G that each node has `k` or more degree within each other.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    k : int
      Value of the decomposition
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.
    peak_number : dictionary, optional
      Precomputed peak numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-peak decomposition

    Raises
    ------
    NetworkXNotImplemented
      The k-peak decomposition is not defined for multigraphs or graphs with self loops.

    See Also
    --------
    peak_number
    core_number

    """
    return nx.k_peak(G, k=k, cores=core_number, peaks=peak_number)


def k_peak_degeneracy(G, core_number=None, peak_number=None):
    """Returns the k-peak degeneracy of G.

    The k-peak degeneracy is the subgraph of G that each node has maximum peak number degree.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.
    peak_number : dictionary, optional
      Precomputed peak numbers for the graph G.

    Returns
    -------
    G : NetworkX graph
      The k-peak degeneracy

    Raises
    ------
    NetworkXNotImplemented
      The k-peak degeneracy is not defined for multigraphs or graphs with self loops.

    Notes
    -----
    K-peak degeneracy is the highest k-peak decomposition.

    See Also
    --------
    peak_number
    core_number
    k_peak_decomposition

    """
    if peaks is None:
        peaks = peak_number(G, cores=core_number)

    k = max(peaks.values())

    return nx.k_peak(G, k=k, cores=core_number, peaks=peak_number)
