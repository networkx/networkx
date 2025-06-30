"""
k-lift graph generator.
This module implements k-lift graph with random permutations,
based on a given d-regular graph.
"""

import random

import networkx as nx


def k_lift(G, k):
    r"""Perform a `k`-lift of a ``d``-regular graph using random permutations.

    The resulting graph H has k copies of each node from G.
    For each edge (u, v) in G, a random permutation is used to connect the i-th copy of u
    to the permuted i-th copy of v in H.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, connected, d-regular graph
    k : int
        The lift parameter. Each node in G is expanded to k copies.

    Returns
    -------
    H : networkx.Graph
        The resulting k-lifted graph.

    Raises
    ------
    ValueError
        If the generated lifted graph is not connected.

    Notes
    -----
    Given a base graph G and a lift parameter k, this function performs a k-lift as follows:
    - For each node v in G, it creates k copies: (v, 0), ..., (v, k-1)
    - For each edge (u, v) in G, a random permutation σ is applied to determine new edges:
      if σ(i) = j, then ((u, i), (v, j)) is added to H.
      The permutation is simulated by creating a shuffled list `permutation` of values 0 to k-1.
      Each i-th copy of u is then connected to the `permutation[i]`-th copy of v.

    References
    ----------
    [1] Y. Bilu and N. Linial. "Lifts, Discrepancy and Nearly Optimal Spectral Gap."
        Combinatorica, 26(5), pp. 495–519, 2006.
        https://www.cs.huji.ac.il/~nati/PAPERS/raman_lift.pdf

    [2] A. Valadarsky, G. Shahaf, M. Dinitz, and M. Schapira.
        "Xpander: Towards Optimal-Performance Datacenters."
        In Proceedings of the 12th International Conference on
        Emerging Networking EXperiments and Technologies (CoNEXT), 2016.
        https://dl.acm.org/doi/pdf/10.1145/2999572.2999580

    Examples
    --------
    >>> import networkx as nx
    >>> from k_lift import k_lift
    >>> d, n, k = 3, 10, 4
    >>> G = nx.random_regular_graph(d, n)
    >>> H = k_lift(G, k)
    >>> H.number_of_nodes()
    40
    """
    H = nx.Graph()

    # Create k copies of each node
    for v in G.nodes:
        for i in range(k):
            H.add_node((v, i))

    # Apply random permutation to edges
    for u, v in G.edges():
        permutation = list(range(k))
        random.shuffle(permutation)
        for i in range(k):
            H.add_edge((u, i), (v, permutation[i]))

    # Raise exception if disconnected
    if not nx.is_connected(H):
        raise ValueError("The lifted graph is not connected")
    return H
