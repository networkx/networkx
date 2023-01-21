import networkx as nx
from networkx.utils import not_implemented_for

@not_implemented_for("directed", "multigraph")
def max_size_envy_free_matching(G, top_nodes=None):
    r"""Return an envy-free matching of maximum cardinality
    Parameters
    ----------
    G:
        NetworkX graph
        Undirected bipartite graph
    top_nodes:
                list
                if graph is not all connected top_nodes is the set of the top nodes in the bipartite graph G
    Returns
    -------
    Matching: dictionary
        The Maximum cardinallity envy-free matching is returned as a dictionary.
    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 2: Finding an envy-free matching of maximum cardinality.

    Examples
    --------
        Example 1: Perfect matching
        >>> Graph=nx.complete_bipartite_graph(3,3)
        >>> max_size_envy_free_matching(Graph)
        {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}

        Where there exists a perfect matching the maximum envy free matching is the perfect matching.
        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> max_size_envy_free_matching(Graph)
        {0: 3, 3: 0}

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> max_size_envy_free_matching(Graph)
        {}

        Like presented in the article, odd path contains an empty envy-free matching so the returned matching is empty.
        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> max_size_envy_free_matching(Graph)
        {}

        Like presented in the article, Y-path-saturated graph contains an empty envy-free matching so X_L and Y_L are empty in the partition.
    """
    M = nx.bipartite.maximum_matching(G, top_nodes=top_nodes)
    EFM_PARTITION = _EFM_partition(G, M, top_nodes)
    un = EFM_PARTITION[1].union(EFM_PARTITION[3])
    M = {node: M[node] for node in M if node not in un and M[node] not in un}
    return M
@not_implemented_for("directed", "multigraph")
def min_weight_max_size_envy_free_matching(G, top_nodes=None):
    r"""Returns minimum-cost maximum-cardinality envy-free matching
    Parameters
    ----------
    G
        NetworkX graph
        Undirected bipartite graph
    top_nodes:
                list
                if graph is not all connected top_nodes is the set of the top nodes in the bipartite graph G
    Returns
    -------
    Matching: dictionary
        The minimum cost maximum cardinallity matching is returned as a dictionary.
    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 3: Finding a minimum-cost maximum-cardinality envy-free matching.

    Examples
    --------
        Example 1: K 3,3 with weights
        >>> G = nx.Graph()
        >>> weights = [(0,3,250), (0,4,148), (0,5,122), (1,3,175), (1,4,135), (1,5,150), (2,3,150), (2,4,125)]
        >>> G.add_weighted_edges_from(weights)
        >>> min_weight_max_size_envy_free_matching(G)
        {0: 5, 1: 4, 2: 3, 5: 0, 4: 1, 3: 2}

        Where there exists a perfect matching the maximum envy free matching is the perfect matching this is the least cost perfect matching.
        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph()
        >>> Graph.add_weighted_edges_from([(0, 4, 5), (1, 4, 1), (2, 5, 3), (2, 7, 9), (3, 6, 3), (3, 7, 7)])
        >>> min_weight_max_size_envy_free_matching(Graph,top_nodes=[0,1,2,3])
        {2: 5, 3: 6, 5: 2, 6: 3}
    """
    M = nx.bipartite.maximum_matching(G, top_nodes=top_nodes)
    EFM_PARTITION = _EFM_partition(G, M, top_nodes)
    Union = EFM_PARTITION[0].union(EFM_PARTITION[2])
    M = nx.bipartite.minimum_weight_full_matching(G.subgraph(Union))
    return M
def __neighbours_of_set__(G, node_set):
    r"""
    returns a set of the neighbours of a given set of nodes
    >>> G = nx.complete_bipartite_graph(3,3)
    >>> __neighbours_of_set__(G, {})
    set()
    >>> __neighbours_of_set__(G, {1, 2})
    {3, 4, 5}

    >>> G = nx.Graph([(0, 4), (1, 5), (2, 6)])
    >>> __neighbours_of_set__(G, {0, 1})
    {4, 5}

    >>> G=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
    >>> __neighbours_of_set__(G, {0, 1})
    {3, 4}

    >>> __neighbours_of_set__(G, {4})
    {0, 1, 2}
    """
    ret_set = {}
    for node in node_set:
        ret_set.update(G[node])

    return set(ret_set)


def __M_alternating_sequence__(G, M, top_nodes=None):
    r"""
    Generates M-alternating-sequence for a graph G with regard to a matching M
    We generate two sets with the following recursive definition:
    X_0 = nodes in G unmatched by M.
    for i>=1:
        Latex:
            Y_i = N_{G\M}(X_{i-1})
            X_i = N_M(Y_i)
        English:
            Y_i -> neighbours of X_{i-1} that were not matched by M group-subtracting all the previous Y_k's we've seen
            X_i -> neighbours of Y_i that were matched by M

    The iterative pattern stops when either Y_k or X_k are an empty set for a certain k, forever staying an empty set from k onward
    the alternating sequece is proven to always stop in the article.

    >>> G = nx.complete_bipartite_graph(3,3)
    >>> M = nx.bipartite.hopcroft_karp_matching(G)
    >>> __M_alternating_sequence__(G, M)
    ((), ())

    >>> G = nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
    >>> M = {0:3, 3:0, 1:4, 4:1}
    >>> __M_alternating_sequence__(G, M)
    (({2}, {1}), ({4},))

    >>> G = nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
    >>> M = {0:3,3:0,4:1,1:4}
    >>> __M_alternating_sequence__(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
    >>> M = {0:3,3:0,4:1,1:4}
    >>> __M_alternating_sequence__(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
    >>> M = {0:6,6:0,1:7,7:1,2:8,8:2,3:9,9:3}
    >>> __M_alternating_sequence__(G, M)
    (({4, 5}, {1, 2, 3}, {0}), ({8, 9, 7}, {6}))

    """
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_0 = set(X) - set(M.keys())
    if X_0 == set():
        return (), ()

    X_subsets = [X_0]
    Y_subsets = []

    Y_subgroups_accumulate = set()
    index = 1

    while len(X_subsets) == 1 or X_subsets[-1] != set() and Y_subsets[-1] != set():
        GMinusM = nx.subgraph_view(
            G,
            filter_edge=lambda u, v: (u, v) not in M.items()
            and (v, u) not in M.items(),
        )
        Y_current = (
            __neighbours_of_set__(GMinusM, X_subsets[-1])
        ) - Y_subgroups_accumulate
        if Y_current == set():
            break
        G_M = nx.subgraph_view(
            G, filter_edge=lambda u, v: (u, v) in M.items() and (v, u) in M.items()
        )
        X_current = __neighbours_of_set__(G_M, Y_current)
        if X_current == set():
            break

        Y_subsets.append(Y_current)
        X_subsets.append(X_current)

        Y_subgroups_accumulate.update(Y_current)
        index += 1

    return tuple(X_subsets), tuple(Y_subsets)


def _EFM_partition(G, M=None, top_nodes=None):
    r"""Returns the unique EFM partition of bipartite graph.

    A matching in a bipartite graph with parts X and Y is called envy-free, if no unmatched
    vertex in X is adjacent to a matched vertex in Y.
    Every bipartite graph has a unique partition such that all envy-free matchings are
    contained in one of the partition set.

    Parameters
    ----------
    G:  NetworkX graph

      Undirected bipartite graph
    M: dict
       dictionary that represents a maximum matching in G.
       If M is none, the function will calculate a maximum matching.
    top_nodes: list
                if graph is not all connected top_nodes is the set of the top nodes in the bipartite graph G

    Returns
    -------
    EFM: tuple of sets
        The partition returns as a tuple of 4 sets of vertices:
        X_L,X_S,Y_L,Y_S where X_L,Y_L are the "good vertices" of G and
        X_S,Y_S are the "bad vertices" of G where no envy-free matching exists according to THM 1.3 in the article.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.

    Examples
    --------
        Example 1: Perfect matching
        >>> Graph=nx.complete_bipartite_graph(3,3)
        >>> Matching=nx.bipartite.hopcroft_karp_matching(Graph)
        >>> _EFM_partition(Graph,Matching)
        ({0, 1, 2}, set(), {3, 4, 5}, set())

        Where there exists a perfect matching the maximum envy free matching is the perfect matching.

        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,1:4,4:1}
        >>> _EFM_partition(Graph,Matching)
        ({0}, {1, 2}, {3}, {4})

        Here the graph contains non-empty envy-free matching so X_L,Y_L are not empty.

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,4:1,1:4}
        >>> _EFM_partition(Graph,Matching)
        (set(), {0, 1, 2}, set(), {3, 4})

        Like presented in the article, odd path contains an empty envy-free matching so X_L and Y_L are empty in the partition.

        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> Matching={0:6,6:0,1:7,7:1,2:8,8:2,3:9,9:3}
        >>> _EFM_partition(Graph,Matching)
        (set(), {0, 1, 2, 3, 4, 5}, set(), {8, 9, 6, 7})

        Like presented in the article, Y-path-saturated graph contains an empty envy-free matching so X_L and Y_L are empty in the partition.

    """
    if M is None:
        M = nx.bipartite.maximum_matching(G, top_nodes=top_nodes)
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_subsets, Y_subsets = __M_alternating_sequence__(G, M, top_nodes)
    X_S = set()
    for subset in X_subsets:
        X_S.update(subset)

    Y_S = set()
    for subset in Y_subsets:
        Y_S.update(subset)

    return set(X) - X_S, X_S, set(Y) - Y_S, Y_S
