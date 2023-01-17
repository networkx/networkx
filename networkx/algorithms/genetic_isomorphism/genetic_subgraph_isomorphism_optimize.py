"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

import concurrent.futures
from networkx.algorithms.genetic_isomorphism.fitness import fitness
import networkx.algorithms.genetic_isomorphism.cython_functions
#from fitness import fitness
# from graph_reduction import build_RG_from_DG
import cython_functions
from math import comb
import networkx as nx
import logging
import concurrent.futures

__all__ = ["find_subgraph_isomorphism_with_genetic_algorithm_cython"]

WORKERS = 4

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log',
                    level=logging.DEBUG, filemode='w')
logger = logging.getLogger()


def find_subgraph_isomorphism_with_genetic_algorithm_cython(G1, G2, ALPHA):
    """
    Since subgraph isomorphism is an NP-hard problem, a
    GA is appropriate. A GA generates a set of initial solutions
    and lets them evolve over a number of iterations. When GA
    meets some condition, the best solution is returned and the
    algorithm terminates. Our algorithm replaces 20 percent
    of the population per generation and uses local optimisation heuristics after crossover and mutation (hybrid or
    memetic GA).

    Improving runtime
    -----------------
    The find_subgraph_isomorphism_with_genetic_algorithm_cython function uses multi-threading and Cython to improve its runtime. 
    Multi-threading distributes the computation across multiple cores, while Cython converts the Python code to faster C code. 
    These optimizations allow for faster execution of the algorithm.

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
    >>> find_subgraph_isomorphism_with_genetic_algorithm_cython(G1, G2, 0)
    True
    """
    logging.info('Started genetic algorithm')
    # Get the nodes of each graph
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    # Calculate the number of combinations of equal size sublists that can be created from the nodes of the two graphs
    num_of_combinations = cython_functions.count_equal_size_combinations(
        G1_nodes, G2_nodes)
    # num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)

    # Generate the solutions
    NUM_OF_SOLUTIONS = int(num_of_combinations / 2)
    if num_of_combinations >= 10000:
        NUM_OF_SOLUTIONS = 10000
    logging.debug(f'Generating {NUM_OF_SOLUTIONS} solutions')
    solutions = []
    # use of multi processes to generate solutions in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
        future_1 = executor.submit(cython_functions.generate_solutions,G1,G2,NUM_OF_SOLUTIONS//2)
        future_2 = executor.submit(cython_functions.generate_solutions,G1,G2,NUM_OF_SOLUTIONS//2)
        for future in concurrent.futures.as_completed([future_1,future_2]):
            r = future.result()
            solutions += r

    # Evaluate the solutions
    NUM_OF_GENERATIONS = int(NUM_OF_SOLUTIONS * 10)
    for i in range(NUM_OF_GENERATIONS):
        logging.debug(f'Evaluating solutions in generation {i+1}')
        found_solution, solutions_with_fitness = cython_functions.evaluate_solutions(
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

        solutions = []
        # Crossover
        logging.debug(f'Performing crossover in generation {i+1}')
        # use of multi processes to crossover solutions in parallel
        with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
            future_1 = executor.submit(cython_functions.crossover,G1_nodes, G2_nodes,
                                               G1_sublists, G2_sublists, NUM_OF_SOLUTIONS//2)
            future_2 = executor.submit(cython_functions.crossover,G1_nodes, G2_nodes,
                                               G1_sublists, G2_sublists, NUM_OF_SOLUTIONS//2)
            for future in concurrent.futures.as_completed([future_1,future_2]):
                r = future.result()
                solutions += r

    return False