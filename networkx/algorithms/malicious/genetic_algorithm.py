"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

# from networkx.algorithms.malicious.fitness import fitness
from math import comb
import random
import networkx as nx

# TODO: add all the functions
# algorithms 1 and 2 in the paper 
__all__ = ["two_vertex_exchange_heuristic", "vertex_relocation_heuristic"]


def count_equal_size_combinations(G1_nodes, G2_nodes):
    # Find the smaller of the two graphs
    smaller_g = G1_nodes if len(G1_nodes) < len(G2_nodes) else G2_nodes

    # Initialize the count to 0
    count = 0

    # Iterate over all subgraph sizes from 0 to the size of the smaller graph
    for i in range(1, len(smaller_g) + 1):
        # Calculate the number of combinations for g1
        g1_combinations = comb(len(G1_nodes), i)

        # Calculate the number of combinations for g2
        g2_combinations = comb(len(G2_nodes), i)

        # Add the total number of combinations for this size to the count
        count += g1_combinations * g2_combinations

    return count


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


def GA(G1, G2, ALPHA=0):
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)
    # calculates the num of combinations
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)
    # generate solutions
    solutions = []
    min_nodes = min(len(G1_nodes), len(G2_nodes))
    NUM_OF_SOLUTIONS = int(num_of_combinations / 4)
    for s in range(NUM_OF_SOLUTIONS):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1_nodes, sub_graph_size)
        sub2 = random.sample(G2_nodes, sub_graph_size)
        solutions.append((sub1, sub2))
    # print("solutions:", solutions)
    NUM_OF_GENERATIONS = NUM_OF_SOLUTIONS * 10
    for i in range(NUM_OF_GENERATIONS):
        rankedsolutions = []  # [solution, fitness' score]
        for s in solutions:
            fitness_score = fitness(G1.subgraph(s[0]), G2.subgraph(s[1]), len(
                G1.nodes), len(G1.edges), len(G2.nodes), len(G2.edges))
            rankedsolutions.append((s, fitness_score))
        # print(f"=== Gen {i+1} best solutions === ")
        # print(rankedsolutions[0])
        # checks if the best solution so fate is less or equals to alpha
        if rankedsolutions[0][1] <= ALPHA:
            # print('--------------------------------------------------------VIRUS-DETECTED--------------------------------------------------------')
            return rankedsolutions[0][1]
            # sorts the solutaions by thier fitness' score
        rankedsolutions = sorted(rankedsolutions, key=lambda x: x[1])
        SOLUTIONS_TO_CHOOSE = int(NUM_OF_SOLUTIONS * 0.8)
        # picks the smallest SOLUTIONS_TO_CHOOSE solutions
        bestsoutions = rankedsolutions[:SOLUTIONS_TO_CHOOSE]
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

        G1_lengths = set([len(lst) for lst in G1_elements])
        # print("G1_lengths:", G1_lengths)
        G2_lengths = set([len(lst) for lst in G2_elements])
        # print("G2_lengths:", G2_lengths)
        intersection = list(G1_lengths.intersection(G2_lengths))

        G1_sublists = {}
        G2_sublists = {}

        for length in intersection:
            G1_sublists[length] = [
                lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [
                lst for lst in G2_elements if len(lst) == length]

        newGen = []
        #[([1,2], [2,3]), fitness]
        count_new_solutions = 0
        while (count_new_solutions < NUM_OF_SOLUTIONS):
            sub_graph_size = random.choice(intersection)
            e1 = random.choice(G1_sublists[sub_graph_size])
            e2 = random.choice(G2_sublists[sub_graph_size])
            # print("(e1, e2):", (e1, e2))
            if (e1, e2) not in newGen:
                newGen.append((e1, e2))
            else:
                new_e1 = random.sample(G1_nodes, sub_graph_size)
                new_e2 = random.sample(G2_nodes, sub_graph_size)
                newGen.append((new_e1, new_e2))
            count_new_solutions += 1

        solutions = newGen
        # print("newGen: ", newGen)
    return rankedsolutions[0][1]
