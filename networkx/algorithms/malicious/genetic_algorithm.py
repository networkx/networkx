"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

__all__ = ["GA", "count_equal_size_combinations"]

from networkx.algorithms.malicious.fitness import fitness
# from fitness import fitness
# from graph_reduction import build_RG_from_DG

from math import comb
import networkx as nx
import logging
import random
import time
import multiprocessing as mp

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log', level=logging.DEBUG, filemode='w')
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

def generate_solutions(G1, G2, num_solutions):
    t_original = time.time()
    # Generate solutions
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))
    for s in range(num_solutions):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1.nodes, sub_graph_size)
        sub2 = random.sample(G2.nodes, sub_graph_size)
        solutions.append((sub1, sub2))
    print("original time:", time.time() - t_original)
    return solutions

def evaluate_solutions(G1, G2, solutions, ALPHA):
    solutions_with_fitness = []
    for i, solution in enumerate(solutions):
        # Calculate the fitness score for the current solution
        fitness_score = fitness(G1.subgraph(solution[0]), G2.subgraph(
            solution[1]), len(G1.nodes), len(G1.edges), len(G2.nodes), len(G2.edges))
        solutions_with_fitness.append((solution, fitness_score))
        # Check if the current solution has a fitness score less than or equal to ALPHA
        if fitness_score <= ALPHA:
            logging.warning(
                f'Found solution with fitness score <= ALPHA ({ALPHA}) in generation {i+1}')
            return True, None
    return False, solutions_with_fitness

def crossover(G1_nodes, G2_nodes, G1_sublists, G2_sublists, num_solutions):
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
    logging.debug(f'Generating new solutions')
    return new_solutions


def GA(G1, G2, ALPHA):
    logging.info('Started genetic algorithm')
    # Get the nodes of each graph
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    # Calculate the number of combinations of equal size sublists that can be created from the nodes of the two graphs
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)

    # Generate the solutions
    NUM_OF_SOLUTIONS = int(num_of_combinations / 2)
    logging.debug(f'Generating {NUM_OF_SOLUTIONS} solutions')
    solutions = generate_solutions(G1, G2, NUM_OF_SOLUTIONS)

    # Evaluate the solutions
    NUM_OF_GENERATIONS = int(NUM_OF_SOLUTIONS * 10)
    for i in range(NUM_OF_GENERATIONS):
        logging.debug(f'Evaluating solutions in generation {i+1}')
        found_solution, solutions_with_fitness = evaluate_solutions(
            G1, G2, solutions, ALPHA)
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
            f'Choosing top {SOLUTIONS_TO_CHOOSE} solutions in generation {i+1}')

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
            G1_sublists[length] = [
                lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [
                lst for lst in G2_elements if len(lst) == length]

        # Crossover
        logging.debug(f'Performing crossover in generation {i+1}')
        solutions = crossover(G1_nodes, G2_nodes,
                              G1_sublists, G2_sublists, NUM_OF_SOLUTIONS)

    return False