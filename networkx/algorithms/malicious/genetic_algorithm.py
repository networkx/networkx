"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
__all__ = ["GA", "count_equal_size_combinations"]

#from networkx.algorithms.malicious.fitness import fitness
from fitness import fitness
from graph_reduction import build_RG_from_DG

from math import comb
import networkx as nx
import logging
import random
import time
import concurrent.futures


LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger()

# =============================Threads===========================

def generate_solutions_multithreading(G1, G2, num_solutions):
    # Generate solutions
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))

    # Create a ThreadPoolExecutor with a maximum number of threads equal to the number of solutions
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Create a list of tasks to pass to the executor
        tasks = []
        for s in range(num_solutions):
            sub_graph_size = random.randint(1, min_nodes)
            sub1 = random.sample(G1.nodes, sub_graph_size)
            sub2 = random.sample(G2.nodes, sub_graph_size)
            task = executor.submit(solutions.append, (sub1, sub2))
            tasks.append(task)

        # Wait for all tasks to complete
        concurrent.futures.wait(tasks)
    return solutions
# ================================================================

# =============================Processes===========================
def generate_solutions_processes(G1, G2, num_solutions):
    # Generate solutions
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))

    # Create a ProcessPoolExecutor with a maximum number of processes equal to the number of solutions
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        # Create a list of tasks to pass to the executor
        tasks = []
        for s in range(num_solutions):
            sub_graph_size = random.randint(1, min_nodes)
            sub1 = random.sample(G1.nodes, sub_graph_size)
            sub2 = random.sample(G2.nodes, sub_graph_size)
            task = executor.submit(solutions.append, (sub1, sub2))
            tasks.append(task)

        # Wait for all tasks to complete
        concurrent.futures.wait(tasks)
    return solutions
# ================================================================


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
    # Generate solutions
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))
    for s in range(num_solutions):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1.nodes, sub_graph_size)
        sub2 = random.sample(G2.nodes, sub_graph_size)
        solutions.append((sub1, sub2))
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
    if num_of_combinations >= 100000:
        NUM_OF_SOLUTIONS = 100000
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

def run_time_simulation(G1, G2, ALPHA, py_func, cython_func, num_of_iterations):
    total_time_py = total_time_cython = 0

    for t in range(num_of_iterations):
        start_time_py = time.time()
        py_func(G1, G2, ALPHA)
        time_py = time.time() - start_time_py
        total_time_py += time_py

        start_time_cython = time.time()
        cython_func(G1, G2, ALPHA)
        time_cython = time.time() - start_time_cython
        total_time_cython += time_cython

    avg_time_py = total_time_py/num_of_iterations
    avg_time_cython = total_time_cython/num_of_iterations
    
    print(f"avg_time_py: {avg_time_py}s")
    print(f"avg_time_cython: {avg_time_cython}s")
    print(f"cython is {avg_time_py / avg_time_cython:.2f} times faster")


def threads_simulation(G1, G2, num_solutions, original_func, threads__func, num_of_iterations):
    total_time_original = total_time_threads = 0

    for t in range(num_of_iterations):
        start_time_original = time.time()
        original_func(G1, G2, num_solutions)
        time_original = time.time() - start_time_original
        total_time_original += time_original

        start_time_threads = time.time()
        threads__func(G1, G2, num_solutions)
        time_threads = time.time() - start_time_threads
        total_time_threads += time_threads

    avg_time_original = total_time_original/num_of_iterations
    avg_time_threads = total_time_threads/num_of_iterations

    print(f"avg_time_original: {avg_time_original}s")
    print(f"avg_time_threads: {avg_time_threads}s")
    print(f"threads is {avg_time_original / avg_time_threads:.2f} times faster")


# def main():
#     # fork code
#     fork_DG = nx.DiGraph()
#     fork_DG.add_nodes_from(range(1, 7))
#     edges = [(1, 2), (2, 3)]
#     fork_DG.add_edges_from(edges)
#     fork_RG = build_RG_from_DG(fork_DG)

#     # fork_code_v1 reduced garph
#     fork_R1_DG = nx.DiGraph()
#     fork_R1_DG.add_nodes_from(range(1, 15))
#     edges = [(1, 4), (2, 6), (3, 5), (4, 7), (5, 8), (5, 10), (10, 10)]
#     fork_R1_DG.add_edges_from(edges)
#     fork_R1_RG = build_RG_from_DG(fork_R1_DG)

#     g1 = nx.gnm_random_graph(5, 8, directed=True)
#     g2 = nx.gnm_random_graph(10, 19, directed=True)    
#     g3 = nx.gnm_random_graph(15, 25, directed=True)    
#     g4 = nx.gnm_random_graph(20, 31, directed=True)

#     g1_RG = build_RG_from_DG(g1)
#     g2_RG = build_RG_from_DG(g2)
#     g3_RG = build_RG_from_DG(g3)
#     g4_RG = build_RG_from_DG(g4)

#     # threads_simulation(G1=fork_RG, G2=fork_R1_RG, num_solutions=10000, original_func=generate_solutions, threads__func=generate_solutions_multithreading, num_of_iterations=10)
    
#     # threads_simulation(G1=fork_RG, G2=fork_R1_RG, num_solutions=10000, original_func=generate_solutions_processes,
#     #                    threads__func=generate_solutions_multithreading, num_of_iterations=10)
# main()
