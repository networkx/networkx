"""
Algorithm to find a maximal (not maximum) independent set.

"""

import networkx as nx
from networkx.utils import not_implemented_for, py_random_state

__all__ = ["maximal_independent_set"]


@not_implemented_for("directed")
@py_random_state(2)
@nx._dispatchable
def maximal_independent_set(G, nodes=None, seed=None):
    """Returns a random maximal independent set guaranteed to contain
    a given set of nodes.

    An independent set is a set of nodes such that the subgraph
    of G induced by these nodes contains no edges. A maximal
    independent set is an independent set such that it is not possible
    to add a new node and still get an independent set.

    Finding an independent set in a graph $G$ is equivalent to
    finding a clique in the complement graph $\bar{G}$.
    Many problems related to independent sets, such as
    finding the maximum independent set, can be solved by applying
    clique algorithms to the complement graph.

    Parameters
    ----------
    G : NetworkX graph

    nodes : list or iterable
       Nodes that must be part of the independent set. This set of nodes
       must be independent.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    indep_nodes : list
       List of nodes that are part of a maximal independent set.

    Raises
    ------
    NetworkXUnfeasible
       If the nodes in the provided list are not part of the graph or
       do not form an independent set, an exception is raised.

    NetworkXNotImplemented
        If `G` is directed.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.maximal_independent_set(G)  # doctest: +SKIP
    [4, 0, 2]
    >>> nx.maximal_independent_set(G, [1])  # doctest: +SKIP
    [1, 3]

    Notes
    -----
    This algorithm is greedy and finds a **maximal** independent set,
    not necessarily a **maximum** independent set. A maximal independent
    set is one where no other node can be added without violating the
    independence property. A maximum independent set is the largest
    possible maximal independent set for the graph.

    To find a maximum independent set, find the maximum clique of the
    complement graph:

    Example
    -------

    >>> G = nx.path_graph(3)
    >>> nx.maximal_independent_set(G, seed=0)
    [1]
    >>> nx.maximal_independent_set(G, seed=1)
    [0, 2]
    >>> G_comp = nx.complement(G)
    >>> nx.clique.max_weight_clique(G_comp, weight=None)
    ([2, 0], 2)

    See Also
    --------
    networkx.algorithms.clique.find_cliques
    networkx.algorithms.clique.max_weight_clique

    """
    if not nodes:
        nodes = {seed.choice(list(G))}
    else:
        nodes = set(nodes)
    if not nodes.issubset(G):
        raise nx.NetworkXUnfeasible(f"{nodes} is not a subset of the nodes of G")
    neighbors = set.union(*[set(G.adj[v]) for v in nodes])
    if set.intersection(neighbors, nodes):
        raise nx.NetworkXUnfeasible(f"{nodes} is not an independent set of G")
    indep_nodes = list(nodes)
    available_nodes = set(G.nodes()).difference(neighbors.union(nodes))
    while available_nodes:
        node = seed.choice(list(available_nodes))
        indep_nodes.append(node)
        available_nodes.difference_update(list(G.adj[node]) + [node])
    return indep_nodes
