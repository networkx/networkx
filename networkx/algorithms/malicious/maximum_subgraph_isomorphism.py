"""
Finding the maximum subgraph isomorphism on two graphs.
"""

__all__ = ["find_max_sub_isomorphism_graph"]

def find_max_sub_isomorphism_graph(G1, G2):
    """
    Finding the maximum subgraph isomorphism on two given (directed) graphs: G1 and G2.
    The function returns the maximum subgraph.

    Parameters
    ----------
    G1 : NetworkX DiGraph
        G2 will compare its subgraphs to this (dirceted) dependency graph
    G2 : NetworkX DiGraph
        All Its subgraphs will be compared to G1 

    Returns
    -------
    G2_tag : NetworkX DiGraph
        A maximum subgraph of G2 that isomorphic to G1

    Notes
    -----
    The problem of maximum subgraph isomorphism is to find
    G_S = (V_S, E_S) which satisfies subgraph isomorphism to G
    if there exists a subgraph G_S ⊂ G = (V,E) while maximizing
    |E_S|/|E|.

    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example 1: finding the maximum subgraph isomorphism on two graphs 
    -----------------------------------------------------------------
    >>> import networkx as nx

    # creates and builds G1 
    >>> G1 = nx.DiGraph()
    >>> directed_G1.add_nodes_from(range(1, 5))
    >>> directed_G1.add_edges_from([(1, 2),(2, 3),(3, 4),(4, 1)])

    # creates and builds G2 
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from(range(1,5))
    >>> G2.add_edges_from([(1, 2),(2, 3),(3, 4),(4, 1),(1, 3),(2, 4)])

    # creates and builds G2_tag
    >>> G2_tag = G1

    >>> find_max_sub_isomorphism_graph(G1, G2)
    G2_tag
    """
    return 0  # Empty implementation
