"""
Finding the number of edges of the maximum subgraph isomorphism on two graphs.
"""

import networkx as nx
from itertools import combinations

__all__ = ["find_max__edges_of_sub_isomorphism_graph"]


def find_max__edges_of_sub_isomorphism_graph(G1, G2):
    """
    Finding the number of edges in the maximum subgraph isomorphism on two given (directed) graphs: G1 and G2.
    The function returns the number of edges of the maximum subgraph.

    Parameters
    ----------
    G1 : NetworkX DiGraph
        This graph will be compare to all G2's subgraphs
    G2 : NetworkX DiGraph
        All Its subgraphs will be compared to G1 

    Returns
    -------
    G2_tag : NetworkX DiGraph
        The number of edges of the maximum subgraph G2' that isomorphic to G1

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

    Example 1: finding the maximum subgraph isomorphism on two graphs (trivial)
    ---------------------------------------------------------------------------
    >>> import networkx as nx

    # creates and builds G1 
    >>> G1 = nx.DiGraph()
    >>> G1.add_nodes_from(range(1, 5))
    >>> G1.add_edges_from([(1, 2),(2, 3),(3, 4),(4, 1)])

    # creates and builds G2 
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from(range(1,5))
    >>> G2.add_edges_from([(1, 2),(2, 3),(3, 4),(4, 1),(1, 3),(2, 4)])

    # creates and builds G2_tag
    >>> G2_tag = G1

    >>> find_max__edges_of_sub_isomorphism_graph(G1, G2)
    4

    Example 2: finding the maximum subgraph isomorphism on two graphs (non trivial)
    -------------------------------------------------------------------------------
    # creates and builds G3 
    >>> G3 = nx.DiGraph()
    >>> G3.add_nodes_from(range(1, 7))
    >>> edges = [(1, 2), (2, 3)]
    >>> G3.add_edges_from(edges)

    # creates and builds G4 
    >>> G4 = nx.DiGraph()
    >>> G4.add_nodes_from(range(1, 15))
    >>> edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
    >>> G4.add_edges_from(edges)

    # creates and builds G4_tag
    >>> G4_tag = nx.DiGraph()
    >>> G4_tag.add_nodes_from(range(1, 6))
    >>> G4_tag.add_node(7)
    >>> edges = [(1, 4), (4, 7), (3, 5)]
    >>> G4_tag.add_edges_from(edges)

    >>> find_max__edges_of_sub_isomorphism_graph(G3, G4)
    2
    """

    # a list of mapping nodes
    max_subgraph = find_max_isomorphism_function(G1, G2)
    # extracts all the keys (G1's nodes) from the dict
    nodes_g1 = list(max_subgraph.keys)
    # extracts all the values (G2's nodes) from the dict
    nodes_g2 = list(max_subgraph.values)
    # calculates the max num of edges between the nodes ????
    min(calculate_num_of_edges(nodes_g1), calculate_num_of_edges(nodes_g2))
    

    return 0  # Empty implementation


# isomorphism function that mapping each node in G1 to its its match node in G2
def find_max_isomorphism_function(G1, G2):
    max_subgraph = [0, 0]  # [0: the subgraph's len, 1: the subgraph]
    subgraphs = nx.algorithms.isomorphism.GraphMatcher(G1, G2)
    for subgraph in subgraphs:
        sub_length = len(subgraph)
        if sub_length > max_subgraph[0]:
            max_subgraph[0] = sub_length
            max_subgraph[1] = subgraph

    return max_subgraph[1]


# the function takes a graph G and a list of nodes, and returns the number of edges between the nodes according to the given graph 
def calculate_num_of_edges(G, nodes):
    num_of_edges = 0
    # iterates over all the possible edges in the graph
    for combo in combinations(nodes, 2):
        if G.has_edge(combo[0], combo[1]):
            num_of_edges += 1
    
    return num_of_edges