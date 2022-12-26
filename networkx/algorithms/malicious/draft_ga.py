"""
Hybrid GA for local optimisation.
Two heuristics to improve the quality of arrangements for maximum subgraph isomorphism.
"""

from networkx.algorithms.malicious.graph_reduction import build_RG_from_DG
from math import comb
import random
import networkx as nx

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


def GA(G1, G2, alpha=0):
    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)
    # calculates the num of combinations
    num_of_combinations = count_equal_size_combinations(G1_nodes, G2_nodes)
    # generate solutions
    solutions = []
    min_nodes = min(len(G1_nodes), len(G2_nodes))
    NUM_OF_SOLUTIONS = int(num_of_combinations / 2)
    for s in range(NUM_OF_SOLUTIONS):
        sub_graph_size = random.randint(1, min_nodes)
        sub1 = random.sample(G1_nodes, sub_graph_size)
        sub2 = random.sample(G2_nodes, sub_graph_size)
        solutions.append((sub1, sub2))
    # print("solutions:", solutions)
    NUM_OF_GENERATIONS = 2000
    for i in range(NUM_OF_GENERATIONS):
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
            G1_sublists[length] = [lst for lst in G1_elements if len(lst) == length]
            G2_sublists[length] = [lst for lst in G2_elements if len(lst) == length]

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


#==============Create-Graphs================
# basic_code reduced garph
basic_RG = nx.DiGraph()
basic_RG.add_nodes_from(range(6, 10))
edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
basic_RG.add_edges_from(edges)

# basic_code_v1 reduced garph
# Variable renaming
basic_RG_v1 = nx.DiGraph()
basic_RG_v1.add_nodes_from(range(6, 10))
edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
basic_RG_v1.add_edges_from(edges)

G1 = nx.DiGraph()
G1.add_nodes_from(range(1, 2))
G1.add_edge(1, 2)
G2 = nx.DiGraph()
G2.add_nodes_from(range(1, 3))
G2.add_edges_from([(1, 2), (2, 3)])

# fork code
fork_DG = nx.DiGraph()
fork_DG.add_nodes_from(range(1, 7))
edges = [(1, 2), (2, 3)]
fork_DG.add_edges_from(edges)
fork_RG = build_RG_from_DG(fork_DG)

ans = GA(basic_RG, fork_RG)
print("ans:", ans)

