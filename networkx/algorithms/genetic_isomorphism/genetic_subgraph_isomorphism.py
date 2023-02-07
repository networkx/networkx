"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

import concurrent.futures
import logging
import random
from math import comb

import networkx as nx
from networkx.algorithms.genetic_isomorphism.fitness import fitness

__all__ = [
    "find_subgraph_isomorphism_with_genetic_algorithm",
    "count_equal_size_combinations",
    "generate_solutions",
    "evaluate_solutions",
    "crossover",
]

WORKERS = 4

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(
    filename="malicious_algo_logging.log", level=logging.INFO, filemode="w"
)
logger = logging.getLogger()


def count_equal_size_combinations(G1_nodes, G2_nodes):
    """
    This is helper method for calculating the number of distinct groups of nodes in equal size

    Parameters
    ---------
    G1_nodes: list of Graph1 nodes
    G2_nodes: list of Graph2 nodes

    Returns
    -------
    The total number of equal size combinations

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example
    -------
    number of disticint possible options
    >>> import networkx as nx
    >>> g1 = nx.gnm_random_graph(3, 3)
    >>> g2 = nx.gnm_random_graph(5, 10)
    >>> g3 = nx.gnm_random_graph(9, 7)
    >>> count_equal_size_combinations(g1,g2)
    55
    >>> count_equal_size_combinations(g1,g3)
    219
    >>> count_equal_size_combinations(g3,g2)
    2001
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
    Generate solutions for matching subgraphs of two given graphs.

    Parameters
    ----------
    - G1 (networkx.Graph): The first graph.
    - G2 (networkx.Graph): The second graph.
    - num_solutions (int): The number of solutions to generate.

    Returns
    -------
    - solutions (list): A list of tuples, each tuple containing two subgraphs (sub1, sub2) from G1 and G2, respectively.

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman
    """
    # Generate solutions
    solutions = []
    min_nodes = min(len(G1.nodes), len(G2.nodes))
    for s in range(num_solutions):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(list(G1.nodes), sub_graph_size)
        sub2 = random.sample(list(G2.nodes), sub_graph_size)
        solutions.append((sub1, sub2))
    return solutions


def evaluate_solutions(G1, G2, solutions, ALPHA):
    """
    Evaluate the solutions for matching subgraphs of two given graphs.

    Parameters
    ----------
    G1 (networkx.Graph): The first graph.
    G2 (networkx.Graph): The second graph.
    solutions (list): A list of tuples, each tuple containing two subgraphs (sub1, sub2) from G1 and G2, respectively.
    ALPHA (float): The threshold value for the fitness score of the solutions.

    Returns
    -------
    flag (bool): A boolean value indicating whether a solution with fitness score less than or equal to ALPHA was found (True) or not (False).
    solutions_with_fitness (list or None): A list of tuples, each tuple containing a solution and its fitness score, if flag is False. If flag is True, it returns None.

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example:
    >>> import networkx as nx
    >>> G1 = nx.Graph()
    >>> G1.add_nodes_from([1, 2, 3, 4, 5])
    >>> G1.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])
    >>> G2 = nx.Graph()
    >>> G2.add_nodes_from([6, 7, 8, 9, 10])
    >>> G2.add_edges_from([(6, 7), (7, 8), (8, 9), (9, 10)])
    >>> solutions = [(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)]
    >>> ALPHA = 0.7
    >>> evaluate_solutions(G1, G2, solutions, ALPHA)
    (False, [((1, 6), 2.0), ((2, 7), 2.0), ((3, 8), 2.0), ((4, 9), 2.0), ((5, 10), 2.0)])
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
                f"Found solution with fitness score {fitness_score} <= ALPHA ({ALPHA}) in generation {i+1}"
            )
            return True, None
    return False, solutions_with_fitness


def crossover(G1_nodes, G2_nodes, G1_sublists, G2_sublists, num_solutions):
    """
    Perform crossover operation to generate new solutions.

    Given two graphs `G1` and `G2` and their sublists of subgraphs `G1_sublists` and `G2_sublists`,
    this function generates `num_solutions` new solutions by performing a crossover operation on the
    sublists. The algorithm first chooses a random sub_graph size from the sublists. Then it chooses
    two subgraphs with the same size randomly from each of the sublists, and combine them to form a
    new solution. If a solution with the same combination already exists, the algorithm generates a
    new pair of subgraphs with the same size and add them to the new solutions.

    Parameters
    ----------
    G1_nodes: A set of nodes in the graph G1.
    G2_nodes: A set of nodes in the graph G2.
    G1_sublists: A dictionary that maps sub_graph_size to a list of subgraphs with the same size
    in G1.
    G2_sublists: A dictionary that maps sub_graph_size to a list of subgraphs with the same size
    in G2.
    num_solutions: An integer that specifies the number of new solutions to generate.

    Returns
    -------
    A list of new solutions, where each solution is a tuple of two subgraphs, one from G1 and one
    from G2.

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman
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
            new_e1 = random.sample(list(G1_nodes), sub_graph_size)
            new_e2 = random.sample(list(G2_nodes), sub_graph_size)
            new_solutions.append((new_e1, new_e2))
        count_new_solutions += 1
    logging.debug(f"Generating new solutions")
    return new_solutions


def find_subgraph_isomorphism_with_genetic_algorithm(G1, G2, ALPHA):
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
    The find_subgraph_isomorphism_with_genetic_algorithm function uses multiprocessing to improve its runtime.
    multiprocessing distributes the computation across multiple cores.
    This optimization allow for faster execution of the algorithm.

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
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example : building a RG graph
    ------------------------------
    >>> import networkx as nx
    >>> G1 = nx.DiGraph()
    >>> G1.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> G1.add_edges_from(edges)
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> G2.add_edges_from(edges)
    >>> find_subgraph_isomorphism_with_genetic_algorithm(G1, G2, 0)
    True
    """
    logging.info("Started genetic algorithm")
    # Get the nodes of each graph
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    # Calculate the number of combinations of equal size sublists that can be created from the nodes of the two graphs
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)
    # num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)

    # Generate the solutions
    NUM_OF_SOLUTIONS = int(num_of_combinations)
    if num_of_combinations >= 10000:
        NUM_OF_SOLUTIONS = 10000
    logging.debug(f"Generating {NUM_OF_SOLUTIONS} solutions")
    solutions = []
    # use of multi processes to generate solutions in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
        future_1 = executor.submit(generate_solutions, G1, G2, NUM_OF_SOLUTIONS // 2)
        future_2 = executor.submit(generate_solutions, G1, G2, NUM_OF_SOLUTIONS // 2)
        for future in concurrent.futures.as_completed([future_1, future_2]):
            r = future.result()
            solutions += r

    # Evaluate the solutions
    NUM_OF_GENERATIONS = int(NUM_OF_SOLUTIONS * 10)
    for i in range(NUM_OF_GENERATIONS):
        logging.debug(f"Evaluating solutions in generation {i+1}")
        found_solution, solutions_with_fitness = evaluate_solutions(
            G1, G2, solutions, ALPHA
        )
        if found_solution:
            return True

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

        G1_lengths = {len(lst) for lst in G1_elements}
        G2_lengths = {len(lst) for lst in G2_elements}
        intersection = list(G1_lengths.intersection(G2_lengths))

        G1_sublists = {}
        G2_sublists = {}

        for length in intersection:
            G1_sublists[length] = [lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [lst for lst in G2_elements if len(lst) == length]

        solutions = []
        # Crossover
        logging.debug(f"Performing crossover in generation {i+1}")
        # use of multi processes to crossover solutions in parallel
        with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
            future_1 = executor.submit(
                crossover,
                G1_nodes,
                G2_nodes,
                G1_sublists,
                G2_sublists,
                NUM_OF_SOLUTIONS // 2,
            )
            future_2 = executor.submit(
                crossover,
                G1_nodes,
                G2_nodes,
                G1_sublists,
                G2_sublists,
                NUM_OF_SOLUTIONS // 2,
            )
            for future in concurrent.futures.as_completed([future_1, future_2]):
                r = future.result()
                solutions += r

    logging.warning(f"Did not find a solution that good enough\n {rankedsolutions[0]}")
    return False
