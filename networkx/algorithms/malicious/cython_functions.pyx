from math import comb
import cython
import random
from networkx.algorithms.malicious.fitness import fitness
from typing import List, Tuple

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef long count_equal_size_combinations(list G1_nodes, list G2_nodes):
    # Find the smaller of the two graphs
    cdef list smaller_g = G1_nodes if len(G1_nodes) < len(G2_nodes) else G2_nodes

    # Initialize the count to 0
    cdef long count = 0

    # Iterate over all subgraph sizes from 0 to the size of the smaller graph
    cdef int i
    cdef long g1_combinations
    cdef long g2_combinations
    for i in range(1, len(smaller_g) + 1):
        # Calculate the number of combinations for g1
        g1_combinations = comb(len(G1_nodes), i)

        # Calculate the number of combinations for g2
        g2_combinations = comb(len(G2_nodes), i)

        # Add the total number of combinations for this size to the count
        count += g1_combinations * g2_combinations
    return count


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef generate_solutions(G1, G2, num_solutions: int):
    cdef list solutions = []
    cdef int min_nodes = min(len(G1.nodes), len(G2.nodes))
    cdef int s
    cdef int sub_graph_size
    cdef list sub1
    cdef list sub2
    for s in range(num_solutions):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1.nodes, sub_graph_size)
        sub2 = random.sample(G2.nodes, sub_graph_size)
        solutions.append((sub1, sub2))
    return solutions


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef evaluate_solutions(G1, G2, solutions: List[Tuple[int, int]], ALPHA: float):
    cdef list solutions_with_fitness = []
    cdef int i
    cdef tuple solution
    cdef float fitness_score
    for i, solution in enumerate(solutions):
        # Calculate the fitness score for the current solution
        fitness_score = fitness(G1.subgraph(solution[0]), G2.subgraph(
            solution[1]), len(G1.nodes), len(G1.edges), len(G2.nodes), len(G2.edges))
        solutions_with_fitness.append((solution, fitness_score))
        # Check if the current solution has a fitness score less than or equal to ALPHA
        if fitness_score <= ALPHA:
            return True, None
    return False, solutions_with_fitness


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef crossover(list G1_nodes, list G2_nodes, dict G1_sublists, dict G2_sublists, int num_solutions):
    cdef list new_solutions = []
    cdef int count_new_solutions = 0
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
    return new_solutions

