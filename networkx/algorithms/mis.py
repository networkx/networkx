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
    indep_nodes : set
       Set of nodes that are part of a maximal independent set.

    Raises
    ------
    NetworkXUnfeasible
       If the nodes in the provided list are not part of the graph or
       do not form an independent set, an exception is raised.

    NetworkXNotImplemented
        If `G` is directed.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> sorted(nx.maximal_independent_set(G, seed=1))
    [1, 3]

    Note that a graph may have many maximal independent sets; for example, the
    path graph with 4 nodes has 3 maximal independent sets: ``{0, 2}``,
    ``{0, 3}`` and ``{1, 3}``.

    >>> sorted(nx.maximal_independent_set(G, seed=2))
    [0, 2]

    This function returns a single maximal independent set. Enumerating *all*
    of the maximal independent sets in a graph can be achieved by enumerating the
    cliques in the complement graph:

    >>> sorted(
    ...     sorted(c)
    ...     for c in nx.enumerate_all_cliques(nx.complement(G))
    ...     if len(c) > 1  # Ignore cliques comprising a single node
    ... )
    [[0, 2], [0, 3], [1, 3]]

    Note however that enumerating all cliques is exponential in the number of
    nodes in the worst case (e.g. the complete graph).

    The `nodes` keyword argument can be used to produce a maximal independent
    set that contains the given node(s):

    >>> sorted(nx.maximal_independent_set(G, nodes={1}))
    [1, 3]

    An exception is raised if `nodes` are not independent

    >>> nx.maximal_independent_set(G, nodes={1, 2})
    Traceback (most recent call last):
       ...
    networkx.exception.NetworkXUnfeasible: {1, 2} is not an independent set of G

    Notes
    -----
    This algorithm does not solve the maximum independent set problem.

    See Also
    --------
    :func:`~networkx.algorithms.approximation.clique.maximum_independent_set` :
        Algorithm for approximating the maximum independent set, i.e. a
        maximal independent set of maximum cardinality.
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
    indep_nodes = set(nodes)
    available_nodes = set(G.nodes()).difference(neighbors.union(nodes))
    while available_nodes:
        node = seed.choice(list(available_nodes))
        indep_nodes.add(node)
        available_nodes.difference_update(list(G.adj[node]) + [node])
    return indep_nodes
