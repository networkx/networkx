import random
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.state import State, update_Tinout, restore_Tinout
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}
    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}

    return T1, T2, T1_out, T2_out


# def main():
# G = nx.gnp_random_graph(20, 0.6, seed=24)

# colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]
#
# for i in range(len(G.nodes)):
#     G.nodes[i]["label"] = colors[random.randrange(len(colors))]
#
# G1_labels = {n: G.nodes[n]["label"] for n in G.nodes()}
# G2_labels = G1_labels

# m = {node: node for node in G.nodes() if node < G.number_of_nodes() // 4}
# s = State(G1=G, G2=G, u=0, node_order=None, mapping=m, reverse_mapping=m)

# cnt = 0
# feasible = -1
# for n in G.nodes():
#     if check_feasibility(node1=0, node2=n, G1=G, G2=G, G1_labels=G1_labels, G2_labels=G2_labels, state=s):
#         feasible = n
#         cnt += 1
#
# print("Number of feasible nodes: ", cnt)
# print("feasible node: ", feasible)

# print(find_candidates(G, G, G1_labels, G2_labels, 452, s))


def main():
    G1 = nx.Graph()
    G2 = nx.Graph()

    G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
    G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

    G1.add_edges_from(G1_edges)
    G2.add_edges_from(G2_edges)
    G1.add_node(0)
    G2.add_node(0)

    mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

    # colors = ["white", "black", "green", "purple", "orange", "red", "blue", "pink", "yellow", "none"]
    # for node, color in zip(G1.nodes, colors):
    #     G1.nodes[node]["label"] = color
    #     G2.nodes[mapped_nodes[node]]["label"] = color

    for n in G1.nodes():
        G1.nodes[n]["label"] = "blue"
        G2.nodes[n]["label"] = "blue"

    G1_labels = {node: G1.nodes[node]["label"] for node in G1.nodes()}
    G2_labels = {node: G2.nodes[node]["label"] for node in G2.nodes()}

    # for node in G1.nodes():
    #     print(f"candidates for node {node}: {check_feasibility(node, mapped_nodes[node], G1, G2, G1_labels, G2_labels, s)}")


main()
