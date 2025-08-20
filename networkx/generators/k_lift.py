"""
k-lift graph generator.
This module implements k-lift graph with random permutations,
based on a given d-regular graph.
"""


import networkx as nx
from networkx.utils import py_random_state


@py_random_state(2)
def k_lift(G, k, seed=None):
    r"""Perform a `k`-lift of a ``d``-regular graph using random permutations.

    The resulting graph ``H`` has `k` copies of each node from `G`.
    For each edge (``u``, ``v``) in `G`, a random permutation is used to connect the ``i``-th copy of ``u``
    to the permuted ``i``-th copy of ``v`` in ``H``.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, connected, ``d``-regular graph.
    k : int
        The lift parameter. Each node in `G` is expanded to `k` copies.
    seed : int, RandomState, or None (default: None)
        Seed for the random number generator (used for permutation generation).
        This ensures reproducibility.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    H : networkx.Graph
        The resulting `k`-lifted graph.

    Raises
    ------
    ValueError
        If `G` is not ``d``-regular or if the generated lifted graph is not connected.

    Notes
    -----
    Given a base graph `G` and a lift parameter `k`, this function performs a `k`-lift as follows:
    - For each node ``v`` in `G`, it creates `k` copies: (``v``, 0), ..., (``v``, `k`-1)
    - For each edge (``u``, ``v``) in `G`, a random permutation σ is applied to determine new edges:
      if σ(``i``) = ``j``, then ((``u``, ``i``), (``v``, ``j``)) is added to ``H``.
      The permutation is simulated by creating a shuffled list ``permutation`` of values 0 to `k`-1.
      Each ``i``-th copy of ``u`` is then connected to the ``permutation[``i``]``-th copy of ``v``.

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
    >>> from networkx.generators.k_lift import k_lift
    >>> G = nx.complete_graph(4)  # 3-regular, connected graph
    >>> H = k_lift(G, 4, seed=42)  # 4-lift of G
    >>> H.number_of_nodes()
    16
    """
    if not nx.is_regular(G):
        raise ValueError("Input graph G must be d-regular.")

    H = nx.Graph()

    # Create k copies of each node
    H.add_nodes_from((v, i) for v in G.nodes for i in range(k))

    # Apply random permutation to edges
    edges = []
    permutation = list(range(k))
    for u, v in G.edges():
        seed.shuffle(permutation)
        edges.extend(((u, i), (v, permutation[i])) for i in range(k))
    H.add_edges_from(edges)

    # Raise exception if disconnected
    if not nx.is_connected(H):
        raise ValueError("The lifted graph is not connected")
    return H
