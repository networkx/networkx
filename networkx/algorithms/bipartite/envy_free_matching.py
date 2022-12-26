
import doctest

import networkx as nx
import networkx
import logging

logging.basicConfig(filename="envy_free_matching.log", level=logging.DEBUG)

__all__ = [
    "envy_free_matching",
    "minimum_weight_envy_free_matching",
]

INFINITY = float("inf")

logger = logging.getLogger("Envy-free matching")
formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: Line %(lineno)d: %(message)s')
console = logging.StreamHandler()  # writes to stderr (= cerr)
logger.handlers = [console]
console.setFormatter(formatter)

def __neighbours_of_set__(G, node_set):
    """
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


def __M_alternating_sequence__(G, M):
    """
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
    X, Y = nx.bipartite.sets(G)

    m_alternating_sequence_logger = logging.getLogger("M_alternating_sequence")
    m_alternating_sequence_logger.info(
        "Starting M_alternating_sequence calculation, used by EFM partition calculation")
    m_alternating_sequence_logger.info(f"G: nodes: {G.nodes}\tedges: {G.edges}")
    m_alternating_sequence_logger.info(f"M: {str(M)}\n")

    X_0 = set(X) - set(M.keys())
    m_alternating_sequence_logger.info(f"Setting X_0 = {X_0} - the vertices of X unmatched by M.")

    if X_0 == set():
        return (), ()

    # GMinusM = nx.subgraph_view(G, filter_edge=lambda u, v: (u,v) not in M.items() and (v, u) not in M.items())
    # Y_0 = __neighbours_of_set__(GMinusM, X_0)
    # m_alternating_sequence_logger.info(f"Setting Y_0 = {Y_0} - Neighbours of X_0 unmatched by M.\n")
    # m_alternating_sequence_logger.info(f"neighbours_of_set__(G, X_0): {str(__neighbours_of_set__(G, X_0))}\n")

    X_subsets = [X_0]
    Y_subsets = []

    Y_subgroups_accumulate = set()
    index = 1

    while len(X_subsets) == 1 or X_subsets[-1] != set() and Y_subsets[-1] != set():
        m_alternating_sequence_logger.info(f"Y_groups accumulation so far: {Y_subgroups_accumulate}\n")

        GMinusM = nx.subgraph_view(G, filter_edge=lambda u, v: (u, v) not in M.items() and (v, u) not in M.items())
        m_alternating_sequence_logger.info(f"G - M: nodes: {GMinusM.nodes}\tedges: {GMinusM.edges}")

        m_alternating_sequence_logger.info(f"N_G - M(X_{index - 1}): {__neighbours_of_set__(GMinusM, X_subsets[-1])}")
        Y_current = (__neighbours_of_set__(GMinusM, X_subsets[-1])) - Y_subgroups_accumulate

        if Y_current == set():
            break

        m_alternating_sequence_logger.info(f"Setting Y_{index} = {Y_current} -> Neighbours of X_{index - 1} "
                                           f"unmatched by M - subtracting from them the Y_groups accumulation.\n")

        G_M = nx.subgraph_view(G, filter_edge=lambda u, v: (u, v) in M.items() and (v, u) in M.items())
        m_alternating_sequence_logger.info(f"G_M: nodes: {G_M.nodes}\tedges: {G_M.edges}")
        X_current = __neighbours_of_set__(G_M, Y_current)

        Y_subsets.append(Y_current)
        X_subsets.append(X_current)

        Y_subgroups_accumulate.update(Y_current)
        index += 1

    return tuple(X_subsets), tuple(Y_subsets)


def _EFM_partition(G, M=None):
    """Returns the unique EFM partition of bipartite graph.

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

    Returns
    -------
    EFM: list of sets
        The partition returns as a list of 4 sets of vertices:
        X_L,X_S,Y_L,Y_S where X_L,Y_L are the "good vertices" of G and
        X_S,Y_S are the "bad vertices" of G where no envy-free matching exists according to THM 1.3 in the article.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.

    Programmers
    -----------
        Benjamin Saldman
        Daniel Gilkarov
    Examples
    --------
        Example 1: Perfect matching
        >>> Graph=nx.complete_bipartite_graph(3,3)
        >>> Matching=nx.bipartite.hopcroft_karp_matching(Graph)
        >>> _EFM_partition(Graph,Matching)
        [{0, 1, 2}, set(), {3, 4, 5}, set()]

        Where there exists a perfect matching the maximum envy free matching is the perfect matching.

        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,1:4,4:1}
        >>> _EFM_partition(Graph,Matching)
        [{0}, {1, 2}, {3}, {4}]

        Here the graph contains non-empty envy-free matching so X_L,Y_L are not empty.

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,4:1,1:4}
        >>> _EFM_partition(Graph,Matching)
        [set(), {0, 1, 2}, set(), {3, 4}]

        Like presented in the article, odd path contains an empty envy-free matching so X_L and Y_L are empty in the partition.

        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> Matching={0:6,6:0,1:7,7:1,2:8,8:2,3:9,9:3}
        >>> _EFM_partition(Graph,Matching)
        [set(), {0, 1, 2, 3, 4, 5}, set(), {8, 9, 6, 7}]

        Like presented in the article, Y-path-saturated graph contains an empty envy-free matching so X_L and Y_L are empty in the partition.

    """

    efm_logger = logging.getLogger("EFM")

    if M is None:
        efm_logger.info("Input matching is None - calculating matching!")

        M = nx.algorithms.bipartite.minimum_weight_full_matching(G)

    X, Y = nx.bipartite.sets(G)

    efm_logger.info(f"Starting EFM_Partition calculation: G={G},\nedges={G.edges}\nX={X}, Y={Y},\nM={M}")
    X_subsets, Y_subsets = __M_alternating_sequence__(G, M)
    X_S = set()
    for subset in X_subsets:
        X_S.update(subset)

    Y_S = set()
    for subset in Y_subsets:
        Y_S.update(subset)

    # return (X_L, X_S, Y_L, Y_S)
    return [set(X) - X_S, X_S, set(Y) - Y_S, Y_S]


def envy_free_matching(G):
    r"""Return an envy-free matching of maximum cardinality
    Parameters
    ----------
    G
        NetworkX graph
        Undirected bipartite graph
    Returns
    -------
    Matching: dictionary
        The Maximum cardinallity envy-free matching is returned as a dictionary.
    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 2: Finding an envy-free matching of maximum cardinality.
    Programmers
    -----------
        Benjamin Saldman
        Daniel Gilkarov
    Examples
    --------
        Example 1: Perfect matching
        >>> Graph=nx.complete_bipartite_graph(3,3)
        >>> envy_free_matching(Graph)
        {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}

        Where there exists a perfect matching the maximum envy free matching is the perfect matching.
        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> envy_free_matching(Graph)
        {0: 3, 3: 0}

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> envy_free_matching(Graph)
        {}

        Like presented in the article, odd path contains an empty envy-free matching so the returned matching is empty.
        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> envy_free_matching(Graph)
        {}

        Like presented in the article, Y-path-saturated graph contains an empty envy-free matching so X_L and Y_L are empty in the partition.
    """
    logger.info(f"Finding the maximum cardinality envy free matching of {G}")
    logger.debug(f"Finding the maximum matching of {G}")
    M = networkx.algorithms.bipartite.hopcroft_karp_matching(G)
    EFM_PARTITION = _EFM_partition(G, M)
    logger.debug(f"Finding the EFM partition with maximum matching: {M}")
    un = EFM_PARTITION[1].union(EFM_PARTITION[3])
    logger.debug(f"Finding the sub-matching M[X_L,Y_L]")
    M = {node: M[node] for node in M if node not in un and M[node] not in un}
    if len(M) == 0:
        logger.warning(f"The sub-matching is empty!")
    logger.debug(f"returning the sub-matching M[X_L,Y_L]: {M}")
    return M
    # return networkx.algorithms.bipartite.hopcroft_karp_matching(G)


def minimum_weight_envy_free_matching(G):
    r"""Returns minimum-cost maximum-cardinality envy-free matching
    Parameters
    ----------
    G
        NetworkX graph
        Undirected bipartite graph
    Returns
    -------
    Matching: dictionary
        The minimum cost maximum cardinallity matching is returned as a dictionary.
    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications to Fair Division",
    by Elad Aigner-Horev and Erel Segal-Halevi (2022), https://arxiv.org/abs/1901.09527
    Algorithm 3: Finding a minimum-cost maximum-cardinality envy-free matching.
    Programmers
    -----------
        Benjamin Saldman
        Daniel Gilkarov
    Examples
    --------
        Example 1: K 3,3 with weights
        >>> Graph=nx.Graph()
        >>> Graph.add_nodes_from([0, 1, 2], bipartite=0)
        >>> Graph.add_nodes_from([3, 4, 5], bipartite=1)
        >>> Graph.add_edge(0,3,weight=250)
        >>> Graph.add_edge(3,0,weight=250)
        >>> Graph.add_edge(0,4,weight=148)
        >>> Graph.add_edge(4,0,weight=148)
        >>> Graph.add_edge(0,5,weight=122)
        >>> Graph.add_edge(5,0,weight=122)
        >>> Graph.add_edge(1,3,weight=175)
        >>> Graph.add_edge(3,0,weight=175)
        >>> Graph.add_edge(1,4,weight=135)
        >>> Graph.add_edge(4,1,weight=135)
        >>> Graph.add_edge(1,5,weight=150)
        >>> Graph.add_edge(5,1,weight=150)
        >>> Graph.add_edge(2,3,weight=150)
        >>> Graph.add_edge(3,2,weight=150)
        >>> Graph.add_edge(2,4,weight=125)
        >>> Graph.add_edge(4,2,weight=125)
        >>> minimum_weight_envy_free_matching(Graph)
        {0: 5, 1: 4, 2: 3, 5: 0, 4: 1, 3: 2}

        Where there exists a perfect matching the maximum envy free matching is the perfect matching this is the least cost perfect matching.
        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph()
        >>> Graph.add_nodes_from([0, 1, 2, 3], bipartite=0)
        >>> Graph.add_nodes_from([4, 5, 6, 7], bipartite=1)
        >>> Graph.add_edge(0,4,weight=5)
        >>> Graph.add_edge(4,0,weight=5)
        >>> Graph.add_edge(1,4,weight=1)
        >>> Graph.add_edge(4,1,weight=1)
        >>> Graph.add_edge(1, 5, weight=500)
        >>> Graph.add_edge(5, 1, weight=500)
        >>> Graph.add_edge(2,5,weight=3)
        >>> Graph.add_edge(5,2,weight=3)
        >>> Graph.add_edge(2,7,weight=9)
        >>> Graph.add_edge(7,2,weight=9)
        >>> Graph.add_edge(3,6,weight=3)
        >>> Graph.add_edge(6,3,weight=3)
        >>> Graph.add_edge(3,7,weight=7)
        >>> Graph.add_edge(7,3,weight=7)
        >>> minimum_weight_envy_free_matching(Graph)
        {0: 4, 1: 5, 2: 7, 3: 6, 4: 0, 5: 1, 7: 2, 6: 3}
    """
    logger.info(f"Finding the minimum cost maximum cardinality envy free matching of {G}")
    logger.debug(f"Finding the maximum matching of {G}")
    M = networkx.algorithms.bipartite.hopcroft_karp_matching(G)
    EFM_PARTITION = _EFM_partition(G, M)
    logger.debug(f"Finding the EFM partition with maximum matching: {M}")
    # EFM_PARTITION = [{2, 3}, {1, 0}, {5, 6, 7}, {4}]
    G.remove_nodes_from((EFM_PARTITION[1]).union((EFM_PARTITION[3])))
    if len((EFM_PARTITION[1]).union((EFM_PARTITION[3]))) == 0:
        logger.warning(f"The sub-matching is empty!")
    M = nx.bipartite.minimum_weight_full_matching(G)
    logger.debug(f"returning minimum cost maximum cardinality envy free matching in G[X_L,Y_L]: {M}")
    return M


if __name__ == '__main__':
    doctest.testmod()


