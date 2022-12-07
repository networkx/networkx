import collections
import itertools

import networkx as nx


__all__ = [
    "envy_free_matching",
    "minimum_weight_envy_free_matching",
]

INFINITY = float("inf")


def _EFM_partition(G, M: dict):
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
        [{0,1,2},{},{3,4,5},{}]

        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,1:4,4:1}
        >>> _EFM_partition(Graph,Matching)
        [{0},{1,2},{3},{4}]

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> Matching={0:3,3:0,4:1,1:4}
        >>> _EFM_partition(Graph,Matching)
        [{},{0,1,2},{},{3,4}]

        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> Matching={0:6,6:0,1:7,7:1,2:8,8:2,3:9,9:3}
        >>> _EFM_partition(Graph,Matching)
        [{},{0,1,2,3,4,5},{},{6,7,8,9}]

    """
    pass


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
        The matching is returned as a dictionary.
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
        {0:3,3:0,1:4,4:1,2:5,5:2}

        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph([(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2)])
        >>> envy_free_matching(Graph)
        {0:3,3:0}

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> envy_free_matching(Graph)
        {}

        Example 3: Odd path
        >>> Graph=nx.Graph([(0,3),(3,0),(1,3),(3,1),(1,4),(4,1),(2,4),(4,2)])
        >>> envy_free_matching(Graph)
        {}

        Example 4: Y-path-saturated graph
        >>> Graph=nx.Graph([(0,6),(6,0),(1,6),(6,1),(1,7),(7,1),(2,6),(6,2),(2,8),(8,2),(3,9),(9,3),(3,6),(6,3),(4,8),(8,4),(4,7),(7,4),(5,9),(9,5)])
        >>> envy_free_matching(Graph)
        {}
    """
    pass


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
        The matching is returned as a dictionary.
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
        >>> Graph.add_edge(3,5,weight=108)
        >>> Graph.add_edge(5,3,weight=108)
        >>> minimum_weight_envy_free_matching(Graph)
        {0:5,5:0,1:4,4:1,2:3,3:2}

        Example 2: Non-empty envy-free matching
        >>> Graph=nx.Graph()
        >>> Graph.add_edge(0,4,weight=5)
        >>> Graph.add_edge(4,0,weight=5)
        >>> Graph.add_edge(1,4,weight=1)
        >>> Graph.add_edge(4,1,weight=1)
        >>> Graph.add_edge(2,5,weight=3)
        >>> Graph.add_edge(5,2,weight=3)
        >>> Graph.add_edge(2,7,weight=9)
        >>> Graph.add_edge(7,2,weight=9)
        >>> Graph.add_edge(3,6,weight=3)
        >>> Graph.add_edge(6,3,weight=3)
        >>> Graph.add_edge(3,7,weight=7)
        >>> Graph.add_edge(7,3,weight=7)
        >>> minimum_weight_envy_free_matching(Graph)
        {2:5,5:2,3:6,6:3}

    """
    pass
