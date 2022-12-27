"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

__all__ = ["GA", "count_equal_size_combinations"]

from networkx.algorithms.malicious.fitness import fitness
from math import comb
import networkx as nx
import logging
import random

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log', level=logging.DEBUG)
logger = logging.getLogger()


def count_equal_size_combinations(G1_nodes, G2_nodes):
    """
    this is helper method for calculating the number of distinct groups of nodes in equal size
    parameter:
    G1_nodes: list of Graph1 nodes
    G2_nodes: list of Graph2 nodes
    return:
    number of disticint possible options
    >>> count_equal_size_combinations(g1,g2)
    34
    >>> count_equal_size_combinations(g1,g3)
    55
    >>> count_equal_size_combinations(g3,g2)
    125
    """

    logging.info('Started counting equal size combinations')
    # Find the smaller of the two graphs
    smaller_g = G1_nodes if len(G1_nodes) < len(G2_nodes) else G2_nodes

    # Initialize the count to 0
    count = 0

    # Iterate over all subgraph sizes from 0 to the size of the smaller graph
    for i in range(1, len(smaller_g) + 1):
        logging.debug(f'Calculating combinations for size {i}')
        # Calculate the number of combinations for g1
        g1_combinations = comb(len(G1_nodes), i)

        # Calculate the number of combinations for g2
        g2_combinations = comb(len(G2_nodes), i)

        # Add the total number of combinations for this size to the count
        count += g1_combinations * g2_combinations
    logging.debug(f'Total number of equal size combinations: {count}')
    return count


def GA(G1, G2, ALPHA):
    """
    Since subgraph isomorphism is an NP-hard problem, a
    GA is appropriate. A GA generates a set of initial solutions
    and lets them evolve over a number of iterations. When GA
    meets some condition, the best solution is returned and the
    algorithm terminates. Our algorithm replaces 20 percent
    of the population per generation and uses local optimisation heuristics after mutation.

    Parameters
    ----------
    G1 : NetworkX DiGraph
        A (dirceted) graph 
    G2 : NetworkX DiGraph
        A (dirceted) graph 
    ALPHA: folat
        A threshold value that indicates how much similar the ftness' score should be

    Returns
    -------
    True iff the minimal fitness' score between all the subgraphs og G1 and G2 it smaller than the given alpha 

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
    >>> G1.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> G1.add_edges_from(edges)

    # creates and builds G2
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> G2.add_edges_from(edges)

    # runs the function
    >>> GA(G1, G2, 0)
    True
    """

    logging.info('Started genetic algorithm')
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)
    # calculates the num of combinations
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)
    # generate solutions
    solutions = []
    min_nodes = min(len(G1_nodes), len(G2_nodes))
    NUM_OF_SOLUTIONS = int(num_of_combinations / 4)
    logging.debug(f'Generating {NUM_OF_SOLUTIONS} solutions')
    for s in range(NUM_OF_SOLUTIONS):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1_nodes, sub_graph_size)
        sub2 = random.sample(G2_nodes, sub_graph_size)
        solutions.append((sub1, sub2))

    num_of_nodes_G1 = len(G1.nodes)
    num_of_edges_G1 = len(G1.edges)
    num_of_nodes_G2 = len(G2.nodes)
    num_of_edges_G2 = len(G2.edges)

    NUM_OF_GENERATIONS = NUM_OF_SOLUTIONS * 2
    for i in range(NUM_OF_GENERATIONS):
        rankedsolutions = []  # [solution, fitness' score]
        logging.debug(f'Evaluating solutions in generation {i+1}')
        for s in solutions:
            fitness_score = fitness(G1.subgraph(s[0]), G2.subgraph(
                s[1]), num_of_nodes_G1, num_of_edges_G1, num_of_nodes_G2, num_of_edges_G2)
            rankedsolutions.append((s, fitness_score))
        # checks if the best solution so fate is less or equals to alpha
        if rankedsolutions[0][1] <= ALPHA:
            logging.warning(
                f'Found solution with fitness score <= ALPHA ({ALPHA}) in generation {i+1}')
            return True
            # sorts the solutaions by thier fitness' score
        rankedsolutions = sorted(rankedsolutions, key=lambda x: x[1])
        logging.debug(f'Sorting solutions in generation {i+1}')
        SOLUTIONS_TO_CHOOSE = int(NUM_OF_SOLUTIONS * 0.8)
        # picks the smallest SOLUTIONS_TO_CHOOSE solutions
        bestsoutions = rankedsolutions[:SOLUTIONS_TO_CHOOSE]
        logging.debug(
            f'Choosing top {SOLUTIONS_TO_CHOOSE} solutions in generation {i+1}')
        G1_elements = []
        G2_elements = []
        for s in bestsoutions:
            G1_sub = s[0][0]  # takes the solution for G1
            G2_sub = s[0][1]  # takes the solution for G2
            G1_elements.append(G1_sub)
            G2_elements.append(G2_sub)

        G1_lengths = set([len(lst) for lst in G1_elements])
        G2_lengths = set([len(lst) for lst in G2_elements])
        intersection = list(G1_lengths.intersection(G2_lengths))

        G1_sublists = {}
        G2_sublists = {}

        for length in intersection:
            G1_sublists[length] = [
                lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [
                lst for lst in G2_elements if len(lst) == length]

        newGen = []
        count_new_solutions = 0
        while (count_new_solutions < NUM_OF_SOLUTIONS):
            sub_graph_size = random.choice(intersection)
            e1 = random.choice(G1_sublists[sub_graph_size])
            e2 = random.choice(G2_sublists[sub_graph_size])
            if (e1, e2) not in newGen:
                newGen.append((e1, e2))
            else:
                new_e1 = random.sample(G1_nodes, sub_graph_size)
                new_e2 = random.sample(G2_nodes, sub_graph_size)
                newGen.append((new_e1, new_e2))
            count_new_solutions += 1
        logging.debug(f'Generating new solutions in generation {i+1}')
        solutions = newGen

    return False
