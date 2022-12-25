import collections
import itertools
import logging
from networkx.algorithms import bipartite

import networkx as nx

__all__ = [
    "envy_free_matching",
    "minimum_weight_envy_free_matching",
]

import networkx.algorithms.bipartite

INFINITY = float("inf")

logger = logging.getLogger("Envy-free matching")
formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: Line %(lineno)d: %(message)s')
console = logging.StreamHandler()  # writes to stderr (= cerr)
logger.handlers = [console]
console.setFormatter(formatter)


def _EFM_partition(G, M=None):
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
       If M is none, the function will find the maximum matching.

    Returns
    -------
    EFM: list of sets
        The partition returns as a list of 4 sets of vertices:
        X_L,X_S,Y_L,Y_S where X_L,Y_L are the "good vertices" of G and
        X_S,Y_S are the "bad vertices" of G.

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
    if M == None:
        M = nx.bipartite.hopcroft_karp_matching(G)
    X, Y = bipartite.sets(G)
    X_0 = {i for i in X if i not in M.keys()}
    G_M = nx.Graph(G)
    G_M.remove_edges_from(M.items())
    # if X_0 == None:
    #     return [X, set(), Y, set()]
    Y_i = set()
    Y_i = {j for i in X_0 for j in G_M.neighbors(i)}
    # for i in X_0:
    #     for j in G_M.neighbors(i):
    #         Y_i.add(j)
    X_i = {M[i] for i in Y_i if i in M.keys()}
    EFM_PARTITION = [set(), X_i.union(X_0), set(), Y_i]
    while len(X_i) != 0 and len(Y_i) != 0:
        # for i in X_i:
        #     for j in G_M.neighbors(i):
        #         Y_i.add(j)
        Y_i = {j for i in X_i for j in G_M.neighbors(i)}
        X_i = {M[i] for i in Y_i if i in M.keys()}
        EFM_PARTITION[1] = EFM_PARTITION[1].union(X_i)
        EFM_PARTITION[3] = EFM_PARTITION[3].union(Y_i)
    Ux = EFM_PARTITION[1]
    Uy = EFM_PARTITION[3]
    return [X - Ux, Ux, Y - Uy, Uy]


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
    logger.setLevel(logging.DEBUG)
    A = nx.Graph()
    # G = nx.Graph()
    # G.add_nodes_from(["a", 2, 3, 4], bipartite=0)
    # G.add_nodes_from([1, "b", "c"], bipartite=1)
    # G.add_edges_from([("a", 1), ("a", "b"), (2, "b"), (2, "c"), (3, "c"), (4, 1)])
    # G.add_edge("a", 1,weight=200)

    A = nx.Graph()
    A.add_nodes_from([0, 1, 2, 3], bipartite=0)
    A.add_nodes_from([4, 5, 6, 7], bipartite=1)
    A.add_edge(0, 4, weight=5)
    A.add_edge(4, 0, weight=5)
    A.add_edge(1, 4, weight=1)
    A.add_edge(4, 1, weight=1)
    A.add_edge(1, 5, weight=500)
    A.add_edge(5, 1, weight=500)
    A.add_edge(2, 5, weight=3)
    A.add_edge(5, 2, weight=3)
    A.add_edge(2, 7, weight=9)
    A.add_edge(7, 2, weight=9)
    A.add_edge(3, 6, weight=3)
    A.add_edge(6, 3, weight=3)
    A.add_edge(3, 7, weight=7)
    A.add_edge(7, 3, weight=7)
    # print(nx.is_bipartite(A))
    # print(nx.is_connected(A))
    # # print(nx.is_bipartite(G))
    # print(minimum_weight_envy_free_matching(A))
    # G = nx.Graph(
    #     [(0, 6), (6, 0), (1, 6), (6, 1), (1, 7), (7, 1), (2, 6), (6, 2), (2, 8), (8, 2), (3, 9), (9, 3), (3, 6), (6, 3),
    #      (4, 8), (8, 4), (4, 7), (7, 4), (5, 9), (9, 5)])
    # print(envy_free_matching(nx.complete_bipartite_graph(3, 3)))
    # A = nx.Graph([(0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1), (2, 4), (4, 2)])
    # A = nx.complete_bipartite_graph(3, 3)
    # A = nx.Graph([(0, 3), (3, 0), (1, 3), (3, 1), (1, 4), (4, 1), (2, 4), (4, 2)])
    # A = nx.Graph(
    #     [(0, 6), (6, 0), (1, 6), (6, 1), (1, 7), (7, 1), (2, 6), (6, 2), (2, 8), (8, 2), (3, 9), (9, 3), (3, 6), (6, 3),
    #      (4, 8), (8, 4), (4, 7), (7, 4), (5, 9), (9, 5)])
    print(nx.bipartite.hopcroft_karp_matching(A))
    print(_EFM_partition(A))
    print(envy_free_matching(A))
    A = nx.Graph()
    A.add_nodes_from([0, 1, 2, 3], bipartite=0)
    A.add_nodes_from([4, 5, 6, 7], bipartite=1)
    A.add_edge(0, 4, weight=5)
    A.add_edge(4, 0, weight=5)
    A.add_edge(1, 4, weight=1)
    A.add_edge(4, 1, weight=1)
    A.add_edge(1, 5, weight=500)
    A.add_edge(5, 1, weight=500)
    A.add_edge(2, 5, weight=3)
    A.add_edge(5, 2, weight=3)
    A.add_edge(2, 7, weight=9)
    A.add_edge(7, 2, weight=9)
    A.add_edge(3, 6, weight=3)
    A.add_edge(6, 3, weight=3)
    A.add_edge(3, 7, weight=7)
    A.add_edge(7, 3, weight=7)
    A = nx.Graph([(0, 4), (4, 0), (0, 5), (5, 0), (0, 8), (8, 0), (1, 6), (6, 1), (2, 7), (7, 2), (3, 7), (7, 3)])

    print(envy_free_matching(A))
