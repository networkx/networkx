"""
Hybrid find_subgraph_isomorphism_with_genetic_algorithm for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

from fitness import fitness
#from networkx.algorithms.genetic_isomorphism.fitness import fitness
#from networkx.algorithms.genetic_isomorphism.graph_reduction import build_RG_from_DG
#from graph_reduction import build_RG_from_DG
from math import comb
import networkx as nx
import logging
import random

__all__ = [
    "find_subgraph_isomorphism_with_genetic_algorithm",
    "count_equal_size_combinations",
    "generate_solutions",
    "evaluate_solutions",
    "crossover",
]

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(
    filename="malicious_algo_logging.log", level=logging.DEBUG, filemode="w"
)
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

    logging.info("Started counting equal size combinations")
    # Find the smaller of the two graphs
    smaller_g = G1_nodes if len(G1_nodes) < len(G2_nodes) else G2_nodes

    # Initialize the count to 0
    count = 0

    # Iterate over all subgraph sizes from 0 to the size of the smaller graph
    for i in range(1, len(smaller_g) + 1):
        logging.debug(f"Calculating combinations for size {i}")
        # Calculate the number of combinations for g1
        g1_combinations = comb(len(G1_nodes), i)

        # Calculate the number of combinations for g2
        g2_combinations = comb(len(G2_nodes), i)

        # Add the total number of combinations for this size to the count
        count += g1_combinations * g2_combinations
    logging.debug(f"Total number of equal size combinations: {count}")
    return count


def generate_solutions(G1, G2, num_solutions):
    """
    This function generate_solutions takes in two input graphs G1 and G2, and an integer num_solutions.
    It generates num_solutions number of random solutions by selecting random sub-graphs of both G1 and G2 with the same number of nodes.
    The function returns a list of tuples, where each tuple contains the solutions of sub-graphs of G1 and G2.
    It uses the python built-in function random.sample to select the random sub-graphs.
    """
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))
    for s in range(num_solutions):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1.nodes, sub_graph_size)
        sub2 = random.sample(G2.nodes, sub_graph_size)
        solutions.append((sub1, sub2))
    return solutions


def evaluate_solutions(G1, G2, solutions, ALPHA):
    """
    This function, evaluate_solutions, calculates the fitness score of each solution in a list of solutions,
    and returns a list of tuples with the solutions and their fitness scores.
    It also checks if any solution's fitness score is less than or equal to a threshold value ALPHA,
    and if so, logs a warning message and returns True, None.
    If all solutions' fitness scores are above ALPHA, it returns False, solutions_with_fitness
    """
    solutions_with_fitness = []
    for i, solution in enumerate(solutions):
        # Calculate the fitness score for the current solution
        fitness_score = fitness(
            G1.subgraph(solution[0]),
            G2.subgraph(solution[1]),
            len(G1.nodes),
            len(G1.edges),
            len(G2.nodes),
            len(G2.edges),
        )
        solutions_with_fitness.append((solution, fitness_score))
        # Check if the current solution has a fitness score less than or equal to ALPHA
        if fitness_score <= ALPHA:
            logging.warning(
                f"Found solution with fitness score <= ALPHA ({ALPHA}) in generation {i+1}"
            )
            return True, None
    return False, solutions_with_fitness


def crossover(G1_nodes, G2_nodes, G1_sublists, G2_sublists, num_solutions):
    """
    This function uses a genetic algorithm to generate new solutions for subgraph isomorphism between two input graphs (G1 and G2).
    It selects random subgraphs of G1 and G2 of the same size, and creates a new solution by pairing them.
    It repeats this process until the desired number of new solutions is reached.
    The new solutions are returned as a list of tuples, each containing a subgraph from G1 and its corresponding subgraph from G2.
    """
    new_solutions = []
    count_new_solutions = 0
    while count_new_solutions < num_solutions:
        sub_graph_size = random.choice(list(G1_sublists.keys()))
        e1 = random.choice(G1_sublists[sub_graph_size])
        e2 = random.choice(G2_sublists[sub_graph_size])
        if (e1, e2) not in new_solutions:
            new_solutions.append((e1, e2))
        else:
            new_e1 = random.sample(G1_nodes, sub_graph_size)
            new_e2 = random.sample(G2_nodes, sub_graph_size)
            new_solutions.append((new_e1, new_e2))
        count_new_solutions += 1
    logging.debug(f"Generating new solutions")
    return new_solutions


def find_subgraph_isomorphism_with_genetic_algorithm(G1, G2, ALPHA):
    """
    Since subgraph isomorphism is an NP-hard problem, a
    find_subgraph_isomorphism_with_genetic_algorithm is appropriate. A find_subgraph_isomorphism_with_genetic_algorithm generates a set of initial solutions
    and lets them evolve over a number of iterations. When find_subgraph_isomorphism_with_genetic_algorithm
    meets some condition, the best solution is returned and the
    algorithm terminates. Our algorithm replaces 20 percent
    of the population per generation and uses local optimisation heuristics after crossover and mutation (hybrid or
    memetic find_subgraph_isomorphism_with_genetic_algorithm).

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
    True iff the minimal fitness' score between all the subgraphs of G1 and G2 it smaller than the given alpha

    Notes
    -----
    In computer science and operations research,
    a genetic algorithm (find_subgraph_isomorphism_with_genetic_algorithm) is a metaheuristic inspired by
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
    >>> find_subgraph_isomorphism_with_genetic_algorithm_C(G1, G2, 0)
    True
    """
    logging.info("Started genetic algorithm")
    # Get the nodes of each graph
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    # Calculate the number of combinations of equal size sublists that can be created from the nodes of the two graphs
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)

    # Generate the solutions
    NUM_OF_SOLUTIONS = int(num_of_combinations / 2)
    if num_of_combinations >= 100000:
        NUM_OF_SOLUTIONS = 100000
    logging.debug(f"Generating {NUM_OF_SOLUTIONS} solutions")
    solutions = generate_solutions(G1, G2, NUM_OF_SOLUTIONS)

    # Evaluate the solutions
    NUM_OF_GENERATIONS = int(NUM_OF_SOLUTIONS * 10)
    for i in range(NUM_OF_GENERATIONS):
        logging.debug(f"Evaluating solutions in generation {i+1}")
        found_solution, solutions_with_fitness = evaluate_solutions(
            G1, G2, solutions, ALPHA
        )
        if found_solution:
            return True

        solutions_with_fitness
        # Sort the solutions by their fitness scores
        rankedsolutions = sorted(solutions_with_fitness, key=lambda x: x[1])
        if NUM_OF_SOLUTIONS == 1:
            SOLUTIONS_TO_CHOOSE = 1
        else:
            SOLUTIONS_TO_CHOOSE = int(NUM_OF_SOLUTIONS * 0.8)
        # Choose the top SOLUTIONS_TO_CHOOSE solutions
        bestsoutions = rankedsolutions[:SOLUTIONS_TO_CHOOSE]
        logging.debug(
            f"Choosing top {SOLUTIONS_TO_CHOOSE} solutions in generation {i+1}"
        )

        G1_elements = []
        G2_elements = []
        for s in bestsoutions:
            G1_sub = s[0][0]  # Take the solution for G1
            G2_sub = s[0][1]  # Take the solution for G2
            G1_elements.append(G1_sub)
            G2_elements.append(G2_sub)

        G1_lengths = set([len(lst) for lst in G1_elements])
        G2_lengths = set([len(lst) for lst in G2_elements])
        intersection = list(G1_lengths.intersection(G2_lengths))

        G1_sublists = {}
        G2_sublists = {}

        for length in intersection:
            G1_sublists[length] = [lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [lst for lst in G2_elements if len(lst) == length]

        # Crossover
        logging.debug(f"Performing crossover in generation {i+1}")
        solutions = crossover(
            G1_nodes, G2_nodes, G1_sublists, G2_sublists, NUM_OF_SOLUTIONS
        )

    return False
