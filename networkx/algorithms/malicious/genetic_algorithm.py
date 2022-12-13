"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

# algorithms 1 and 2 in the paper
__all__ = ["two_vertex_exchange_heuristic", "vertex_relocation_heuristic"]


def two_vertex_exchange_heuristic(G):
    """
    The algorithm, exchanges the locations of two vertices if the change causes an improvement.
    There exist θ(|V|^2) combinations of selecting two vertices.

    Parameters
    ----------
    G : NetworkX DiGraph
        A (dirceted) graph 

    Returns
    -------
    G : NetworkX DiGraph
        The same graph after the exganges  

    Notes
    -----
    In computer science and operations research, 
    a genetic algorithm (GA) is a metaheuristic inspired by 
    the process of natural selection that belongs to the larger
    class of evolutionary algorithms (EA). 
    Genetic algorithms are commonly used to generate high-quality
    solutions to optimization and search problems by relying on 
    biologically inspired operators such as mutation, crossover and selection.

    https://en.wikipedia.org/wiki/Genetic_algorithm

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    Algorithm 1, page 5.
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example : building a RG graph
    ------------------------------
    >>> import networkx as nx

    # creates and builds G1 
    >>> G1 = nx.DiGraph()
    >>> nodes = [7, 6, 8, 9, 10]
    >>> G1.add_nodes_from(nodes)
    >>> edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9), (10, 7), (10, 8), (10, 9), (10, 10)]
    >>> G1.add_edges_from(edges)

    # creates and builds G2 (G1 after the swap between nodes 8 and 10)
    >>> G2 = nx.DiGraph()
    >>> nodes = [7, 6, 10, 9, 8]
    >>> G2.add_nodes_from(nodes)
    >>> edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9), (10, 7), (10, 8), (10, 9), (10, 10)]
    >>> G2.add_edges_from(edges)

    # runs the function
    >>> two_vertex_exchange_heuristic(G1)
    >>> G1.nodes == G2.nodes and G1.edges == G2.edges
    True
    """
    return 0  # Empty implementation


def vertex_relocation_heuristic(G):
    """
    For every vertex, the algorithm tries to find the optimal location.
    A new solution is taken if relocation of the vertex into another location improves the fitness. 
    There exist V vertices to move and V−1 possible locations for each vertex.

    Parameters
    ----------
    G : NetworkX DiGraph
        A (dirceted) graph 

    Returns
    -------
    G : NetworkX DiGraph
        The same graph after the exganges  

    Notes
    -----
    In computer science and operations research, 
    a genetic algorithm (GA) is a metaheuristic inspired by 
    the process of natural selection that belongs to the larger
    class of evolutionary algorithms (EA). 
    Genetic algorithms are commonly used to generate high-quality
    solutions to optimization and search problems by relying on 
    biologically inspired operators such as mutation, crossover and selection.

    https://en.wikipedia.org/wiki/Genetic_algorithm

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    Algorithm 2, page 5-6.
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example : building a RG graph
    ------------------------------
    >>> import networkx as nx

    # creates and builds G1 
    >>> G1 = nx.DiGraph()
    >>> nodes = [7, 8, 6, 10, 9]
    >>> G1.add_nodes_from(nodes)
    >>> edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9), (10, 7), (10, 8), (10, 9), (10, 10)]
    >>> G1.add_edges_from(edges)

    # creates and builds G2 (G1 after the swap between nodes 8 and 10)
    >>> G2 = nx.DiGraph()
    >>> nodes = [7, 6, 10, 9, 8]
    >>> G2.add_nodes_from(nodes)
    >>> edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9), (10, 7), (10, 8), (10, 9), (10, 10)]
    >>> G2.add_edges_from(edges)

    # runs the function
    >>> vertex_relocation_heuristic(G1)
    >>> G1.nodes == G2.nodes and G1.edges == G2.edges
    True
    """
    return 0  # Empty implementation
