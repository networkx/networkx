"""Semiconnectedness."""
import networkx as nx
from networkx.utils import not_implemented_for, pairwise

__all__ = ["is_semiconnected"]


@not_implemented_for("undirected")
def is_semiconnected(G, topo_order=None):
    """Returns True if the graph is semiconnected, False otherwise.

    A graph is semiconnected if, and only if, for any pair of nodes, either one
    is reachable from the other, or they are mutually reachable.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph.

    topo_order: list or tuple, optional
        .. warning:: Do not use

           `topo_order` gives incorrect results and will be removed in the
           future. Non-default values will result in an exception.

    Returns
    -------
    semiconnected : bool
        True if the graph is semiconnected, False otherwise.

    Raises
    ------
    NetworkXNotImplemented
        If the input graph is undirected.

    NetworkXPointlessConcept
        If the graph is empty.

    Examples
    --------
    >>> G = nx.path_graph(4, create_using=nx.DiGraph())
    >>> print(nx.is_semiconnected(G))
    True
    >>> G = nx.DiGraph([(1, 2), (3, 2)])
    >>> print(nx.is_semiconnected(G))
    False

    See Also
    --------
    is_strongly_connected
    is_weakly_connected
    is_connected
    is_biconnected
    """
    if topo_order is not None:
        raise TypeError(
            "`topo_order` gives incorrect results and is no longer supported."
            "\nRemove `topo_order` from the function call."
        )

    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "Connectivity is undefined for the null graph."
        )

    if not nx.is_weakly_connected(G):
        return False

    H = nx.condensation(G)

    return all(H.has_edge(u, v) for u, v in pairwise(nx.topological_sort(H)))
