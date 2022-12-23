"""
Calculates the fitness function between two graphs.
"""

__all__ = ["calculate_fitness"]

def calculate_fitness(G1, G2):
    """
    Measures the proportion of the number of different edges
    between two given graphs against the number of edges in the
    smaller graph, to evaluate a chromosome. That will be called the
    difference, noted by d, of the graphs. The difference value 0
    means that G2 is a complete subgraph of G1.
    The function returns the difference.

    Parameters
    ----------
    G1 = (V1, E1), G2 = (V2, E2), and |V1|≤|V2|.
    G1 : NetworkX DiGraph
        G1 is a dirceted graph, G1 = (V1, E1), G1 is the smaller garph
    G2 : NetworkX DiGraph
        G2 is a dirceted graph, G2 = (V2, E2), G2 is the bigger graph
    Note: |V1|≤|V2|.

    Returns
    -------
    difference : flaot
        The results of the fitness function.
        The smaller the value, the higher the fitness.

    Notes
    -----
    A fitness function is a particular type of objective function that is used to summarise,
    as a single figure of merit, how close a given design solution is to achieving the set aims.
    Fitness functions are used in genetic programming and genetic algorithms to guide
    simulations towards optimal design solutions.

    https://en.wikipedia.org/wiki/Fitness_function
    
    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example: finding the maximum subgraph isomorphism on two graphs 
    -----------------------------------------------------------------
    >>> import networkx as nx

    # creates and builds G1 
    >>> G1 = nx.DiGraph()
    >>> directed_G1.add_nodes_from(range(1, 7))
    >>> directed_G1.add_edges_from([(1, 2),(2, 3),(3, 4)])

    # creates and builds G2 
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from(range(1,15))
    >>> G2.add_edges_from([(1, 4),(2, 6),(3, 5),(4, 7),(5, 8),(5, 10),(10,10)])

    # runs the function
    >>> calculate_fitness(G1, G2)
    2.5
    """

    import networkx as nx
    # calculate fitness function
    # first, find isomoprphism between fork_v2 to fork_v1
    subG = {}
    GM = nx.algorithms.isomorphism.GraphMatcher(G2, G1)
    for subgraph in GM.subgraph_isomorphisms_iter():
        if len(subgraph) > len(subG):
            subG = subgraph
    # print(subG)

    # extract the nodes
    nG2 = list(subG.keys())
    nG1 = list(subG.values())
    # print(nG1, nG2)

    # Extract a subgraph containing nodes the fit nodes from fork_v2 to fork_v1
    subgraph = nx.subgraph(G1, nG1)
    # print("-----------------\n", subgraph.edges)
    # print(subgraph.nodes)

    # Print the subgraph's edges
    diff_1 = len(G2.edges) - len(subgraph.edges)
    diff_2 = len(G1.edges) - len(subgraph.edges)
    fitness = (diff_1 + diff_2) / len(G1.edges)

    return fitness  


import networkx as nx
# create two graphs
G1 = nx.DiGraph()
G1.add_nodes_from(range(1, 7))
edges = [(1, 2), (2, 3)]
G1.add_edges_from(edges)
G2 = nx.DiGraph()
G2.add_nodes_from(range(1, 15))
edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
G2.add_edges_from(edges)

ans = calculate_fitness(G1, G2)
print("ans:", ans)

