"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

# from networkx.algorithms.malicious.fitness import fitness
import random
import networkx as nx

# algorithms 1 and 2 in the paper
__all__ = ["two_vertex_exchange_heuristic", "vertex_relocation_heuristic"]


def fitness(sub_G1, sub_G2, G1_nodes, G1_edges, G2_nodes, G2_edges):
    """
    fitness function to calculate the quality of the solution
    given two sub graphs, and the original graphs size
    """
    if nx.is_isomorphic(sub_G1, sub_G2):
        min_val = 0
        if G1_nodes < G2_nodes:
            min_val = G1_edges
        else:
            min_val = G2_edges
        mutual = len(sub_G2.edges)
        return (((G1_edges - mutual) + (G2_edges - mutual)) / min_val)
    else:
        return 999999


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


def GA(G1, G2, alpha=0.5):
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)
    # generate solutions
    solutions = []
    min_nodes = min(len(G1_nodes), len(G2_nodes))
    NUM_OF_SOLUTIONS = 10
    for s in range(NUM_OF_SOLUTIONS):
        num = random.randint(1, min_nodes)
        sub1 = set(random.sample(G1_nodes, num))
        sub2 = set(random.sample(G2_nodes, num))
        solutions.append((sub1, sub2))
    # print(solutions)
    NUM_OF_GENERATIONS = 100
    for i in range(NUM_OF_GENERATIONS):
        # print(solutions)
        rankedsolutions = []  # [solution, fitness' score]
        for s in solutions:
            fitness_score = fitness(G1.subgraph(s[0]), G2.subgraph(s[1]), len(
                G1.nodes), len(G1.edges), len(G2.nodes), len(G2.edges))
            rankedsolutions.append((s, fitness_score))
        # print(f"=== Gen {i+1} best solutions === ")
        # print(rankedsolutions[0])
        # checks if the best solution so fate is less or equals to alpha
        if rankedsolutions[0][1] <= alpha:
            # print('--------------------------------------------------------VIRUS-DETECTED--------------------------------------------------------')
            return rankedsolutions[0][1]
            # sorts the solutaions by thier fitness' score
        rankedsolutions = sorted(rankedsolutions, key=lambda x: x[1])
        # picks the smallest 100 solutions
        bestsoutions = rankedsolutions[:100]
        G1_elements = []
        G2_elements = []
        for s in bestsoutions:
            # print("s:", s)
            G1_sub = s[0][0]  # takes the solution for G1
            G2_sub = s[0][1]  # takes the solution for G2
            G1_elements.append(G1_sub)
            G2_elements.append(G2_sub)
        # print("G1_elements:", G1_elements)
        # print("G2_elements:", G2_elements)
        newGen = []
        #[([1,2], [2,3]), fitness]
        count_new_solutions = 0
        TIME_OUT = 200
        while (count_new_solutions < NUM_OF_SOLUTIONS or TIME_OUT != 0):
            TIME_OUT = - 1
            # print(count_new_solutions)
            e1 = random.choice(list(G1_elements))
            e2 = random.choice(list(G2_elements))
            # print("e:", e1, e2)
            if (len(e1) == len(e2)) and (e1, e2) not in newGen:
                newGen.append((e1, e2))
                count_new_solutions += 1
        # print("newGen:", newGen)
        solutions = newGen
    return rankedsolutions[0][1]
