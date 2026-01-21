import itertools as it

import networkx as nx
from networkx.algorithms.bipartite.matching import (
    maximum_matching,
    minimum_weight_full_matching,
)

__all__ = [
    "envy_free_matching_partition",
    "maximum_envy_free_matching",
    "minimum_weight_envy_free_matching",
]


def _M_alternating_sequence(G, M, *, top_nodes=None):
    r"""Return an M-alternating-sequence of a bipartite graph `G` with
    regard to a matching `M`.

    An *M-alternating-sequence* is a sequence of pairwise disjoint subsets of nodes X_0 - Y_1 - X_1 - Y_2 - X_2 - ...
    When `M` is a maximum matching, the M-alternating-sequence calculated using it has some useful properties for
    finding envy free bipartite matching, this is proved in the article.

    Two sets are calculated with the following recursive definition:

    X_0 = nodes in G unmatched by M.
    for i>=1:
        Latex:
            Y_i = :math:`N_{G\M}(X_{i-1})\\`
            X_i = :math:`N_M(Y_i)`
        English:
            Y_i -> neighbors of X_{i-1} that were not matched by M
                   group-subtracting all the previous Y_k's we've seen
            X_i -> neighbors of Y_i that were matched by M

    The iterative pattern stops when either Y_k or X_k are an empty set for a
    certain k, forever staying an empty set. From k onward the alternating sequence
    is proven to always stop in the article.

    Two tuples containing sets of nodes are returned - tuple(X_subsets), tuple(Y_subsets).

    >>> G = nx.complete_bipartite_graph(3, 3)
    >>> M = nx.bipartite.hopcroft_karp_matching(G)
    >>> _M_alternating_sequence(G, M)
    ((), ())

    >>> G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 1: 4, 4: 1}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}), ({4},))

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 4: 1, 1: 4}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 4: 1, 1: 4}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph(
    ...     [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    ... )
    >>> M = {0: 6, 6: 0, 1: 7, 7: 1, 2: 8, 8: 2, 3: 9, 9: 3}
    >>> _M_alternating_sequence(G, M)
    (({4, 5}, {1, 2, 3}, {0}), ({8, 9, 7}, {6}))

    """
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_0 = set(X) - set(M.keys())
    if len(X_0) == 0:
        return (), ()

    X_subsets = [X_0]
    Y_subsets = []

    Y_subgroups_accumulate = set()

    while len(X_subsets) == 1 or (len(X_subsets[-1]) != 0 and len(Y_subsets[-1]) != 0):
        Y_current = {
            nbr
            for n in X_subsets[-1]
            for nbr in G[n]
            if nbr not in Y_subgroups_accumulate
            if M.get(n) != nbr
            if M.get(nbr) != n
        }
        if len(Y_current) == 0:
            break
        X_current = {
            nbr
            for n in Y_current
            for nbr in G[n]
            if M.get(n) == nbr and M.get(nbr) == n
        }
        if len(X_current) == 0:
            break

        Y_subsets.append(Y_current)
        X_subsets.append(X_current)

        Y_subgroups_accumulate.update(Y_current)

    return tuple(X_subsets), tuple(Y_subsets)


def envy_free_matching_partition(G, *, M=None, top_nodes=None):
    r"""Return a unique EFM (Envy Free Matching) partition of bipartite graph `G`.

    An EFM partition of a bipartite graph with bipartite sets X,Y is a unique partition of X - X_L, X_S and Y - Y_L, Y_S.
    This unique partition is proven to have the following properties:
    1. Every matching that matches all the nodes in X_L and is contained in G[X_L,Y_L] (all edges are between X_L and Y_L)
    is an envy-free matching.
    2. Every envy-free matching in `G` is contained in G[X_L,Y_L].

    Due to these properties we can say that X_L and Y_L are the "*good*" nodes and X_S and Y_S are the "*bad*" nodes,
    because - in the context of finding envy-free matchings, we will only find them in X_L and Y_L.

    Parameters
    ----------
    G:  NetworkX graph
      Undirected bipartite graph

    M: dict
      dictionary that represents a maximum matching in `G`.
      If M is none, the function will calculate a maximum matching.

    top_nodes: list
      if graph is not all connected top_nodes is the set of the top nodes in
      the bipartite graph `G`.

    Returns
    -------
    EFM: tuple of sets
      The partition returns as a tuple of 4 sets of nodes:
      `(X_L, X_S, Y_L, Y_S)` where X_L and Y_L are the "good nodes" of G
      while X_S and Y_S are the "bad nodes" of G where no envy-free matching
      exists according to THM 1.3 in the article.

    Examples
    --------
    Example 1: Perfect matching

    >>> G = nx.complete_bipartite_graph(3, 3)
    >>> M = nx.bipartite.hopcroft_karp_matching(G)
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    ({0, 1, 2}, set(), {3, 4, 5}, set())

    Where there exists a perfect matching the maximum cardinality
    envy free matching is the perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 1: 4, 4: 1}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    ({0}, {1, 2}, {3}, {4})

    Here the graph contains a non-empty envy-free matching so X_L and Y_L are not empty.

    Example 3: Odd path

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 4: 1, 1: 4}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    (set(), {0, 1, 2}, set(), {3, 4})

    Like presented in the article, odd path contains an empty envy-free matching
    so X_L and Y_L are empty in the partition.

    Example 4: Y-path-saturated graph

    >>> G = nx.Graph(
    ...     [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    ... )
    >>> M = {0: 6, 6: 0, 1: 7, 7: 1, 2: 8, 8: 2, 3: 9, 9: 3}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    (set(), {0, 1, 2, 3, 4, 5}, set(), {8, 9, 6, 7})

    Like presented in the article [1], Y-path-saturated graph contains an empty
    envy-free matching so X_L and Y_L are empty in the partition.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    if M is None:
        M = maximum_matching(G, top_nodes=top_nodes)
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_subsets, Y_subsets = _M_alternating_sequence(G, M, top_nodes=top_nodes)
    X_S = set(it.chain.from_iterable(X_subsets))
    Y_S = set(it.chain.from_iterable(Y_subsets))
    return set(X) - X_S, X_S, set(Y) - Y_S, Y_S


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def maximum_envy_free_matching(G, *, top_nodes=None):
    r"""Return an envy-free matching of maximum cardinality of the bipartite graph `G`

    A matching in a bipartite graph with bipartite sets X and Y is called envy-free,
    if no unmatched node in X is adjacent to a matched node in Y.

    An envy-free bipartite matching has *maximum cardinality* if it is the largest (has the most edges) possible matching
    that is still envy-free.
    There can be multiple different envy-free matching of maximum cardinality, this function returns *one* of them.

    There are graphs which don't have any possible envy-free matching or synonmously,
    their largest envy-free bipartite matching is empty.

    Envy-Free bipartite matches can be used for matching between people to "things" in a fair way.
    For example, they can be used for House Allocation Problems.

    Illustration: A real estate agent has a group of buyers seeking to purchase a house and a group of houses for sale,
    each buyer indicated houses they are interested in. The real estate agent wants to maximize the amount of people
    that get a house and avoid making customers that didn't get a house jealous by giving other customers houses they
    were interested in.

    this problem can be modeled to a bipartite graph with the buyers set (X), houses set(Y) and edges
    between X and Y indicating a buyer being interested in a house (binary "yes" or "no"). Using networkx, you can construct a bipartite graph
    as described, and call "maximum_envy_free_matching" on it to receive a matching of buyers to houses, guarenteed to
    be fair (This can produce an empty matching - meaning fairness can't be achieved in this case).


    Parameters
    ----------
    G : NetworkX graph
      Undirected bipartite graph

    top_nodes : container
      If graph is not connected `top_nodes` is the set of the top nodes in
      the bipartite graph `G`.

    Returns
    -------
    Matching: dictionary
        A Maximum cardinality envy-free matching is returned as a dictionary.

    Examples
    --------
    Example 1: Perfect matching

    >>> G = nx.complete_bipartite_graph(3, 3)
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}

    Where there exists a perfect matching the maximum envy free matching is
    the perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {0: 3, 3: 0}

    Example 3: Odd path

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {}

    Like presented in the article, an odd path contains an empty envy-free matching
    so the returned matching is empty.

    Example 4: Y-path-saturated graph

    >>> G = nx.Graph(
    ...     [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    ... )
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {}

    Like presented in the article [1]_, Y-path-saturated graph contains an empty
    envy-free matching so X_L and Y_L are empty in the partition.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    M = maximum_matching(G, top_nodes=top_nodes)
    partition = envy_free_matching_partition(G, M=M, top_nodes=top_nodes)
    un = partition[1].union(partition[3])
    return {node: M[node] for node in M if node not in un and M[node] not in un}


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def minimum_weight_envy_free_matching(G, *, top_nodes=None):
    r"""Returns a minimum weight maximum cardinality envy-free matching of the bipartite graph `G`

    A matching in a bipartite graph with bipartite sets X and Y is called envy-free,
    if no unmatched node in X is adjacent to a matched node in Y.

    An envy-free bipartite matching has *maximum cardinality* if it is the largest (has the most edges) possible matching
    that is still envy-free.
    This function returns an envy-free bipartite matching with the least cost (sum of edge weights) out of the maximum cardinality matchings.

    There can be multiple different envy-free matching of maximum cardinality and minimum weight, this function returns *one* of them.

    Weighted Envy-Free bipartite matches can be used for matching between people to "things" in a fair way considering cardinal preferences.
    For example, they can be used for the Rental harmony problem.

    Illustration: A group of people that want to rent an apartament as roomates want to find a pairing of roomate to room and minimize cost for each one.
    Each roomate assign an amount he's willing to pay for a certain room.

    this problem can be modeled to a bipartite graph with the roomates set (X), rooms set(Y) and edges
    between X and Y indicating a roomate interested in a room and the edge weight meaning the amount of money he's willing to pay.
    Using networkx, you can construct a bipartite graph
    as described, and call "minimum_weight_envy_free_matching" on it to receive a matching of roomates to rooms, guarenteed to
    be fair (This can produce an empty matching - meaning fairness can't be achieved in this case).



    Parameters
    ----------
    G : NetworkX graph
      Undirected bipartite graph.

    top_nodes : container
      If graph is not connected `top_nodes` is the set of the top nodes
      in the bipartite graph `G`.

    Returns
    -------
    Matching: dictionary
      A minimum weight maximum cardinality matching is returned as a dictionary.

    Examples
    --------
    Example 1: K 3,3 with weights

    >>> G = nx.Graph()
    >>> edges = [
    ...     (0, 3, 250),
    ...     (0, 4, 148),
    ...     (0, 5, 122),
    ...     (1, 3, 175),
    ...     (1, 4, 135),
    ...     (1, 5, 150),
    ...     (2, 3, 150),
    ...     (2, 4, 125),
    ... ]
    >>> G.add_weighted_edges_from(edges)
    >>> nx.bipartite.minimum_weight_envy_free_matching(G)
    {0: 5, 1: 4, 2: 3, 5: 0, 4: 1, 3: 2}

    Where there exists a perfect matching the maximum envy free matching is a
    perfect matching and this is the minimum weight perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph()
    >>> edges = [(0, 4, 5), (1, 4, 1), (2, 5, 3), (2, 7, 9), (3, 6, 3), (3, 7, 7)]
    >>> G.add_weighted_edges_from(edges)
    >>> nx.bipartite.minimum_weight_envy_free_matching(G, top_nodes=[0, 1, 2, 3])
    {2: 5, 3: 6, 5: 2, 6: 3}

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    M = maximum_matching(G, top_nodes=top_nodes)
    partition = envy_free_matching_partition(G, M=M, top_nodes=top_nodes)
    union_partition = partition[0].union(partition[2])
    return minimum_weight_full_matching(G.subgraph(union_partition))
