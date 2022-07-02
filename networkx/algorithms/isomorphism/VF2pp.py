import random
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.state import State, update_Tinout
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}
    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}

    return T1, T2, T1_out, T2_out


def main():
    G = nx.gnp_random_graph(20, 0.6, seed=24)

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

    mapping = dict()
    reverse_mapping = dict()

    T1 = set()
    T2 = set()
    T1_out = set(G.nodes())
    T2_out = set(G.nodes())

    slow_T1, slow_T2, slow_T1_out, slow_T2_out = compute_Ti(G, G, mapping, reverse_mapping)

    print(slow_T1)
    print(slow_T2)
    print(slow_T1_out)
    print(slow_T2_out)

    # Insert new nodes in the mapping
    print("After mapping nodes 0-0")

    mapping.update({0: 0})
    reverse_mapping.update({0: 0})
    T1, T2, T1_out, T2_out = update_Tinout(G, G, T1, T2, T1_out, T2_out, 0, 0, mapping, reverse_mapping)

    print("fast")
    print(T1)
    print(T2)
    print(T1_out)
    print(T2_out)

    slow_T1, slow_T2, slow_T1_out, slow_T2_out = compute_Ti(G, G, mapping, reverse_mapping)

    print("slow")
    print(slow_T1)
    print(slow_T2)
    print(slow_T1_out)
    print(slow_T2_out)

    print("After mapping nodes 5-5")

    mapping.update({5: 5})
    reverse_mapping.update({5: 5})
    T1, T2, T1_out, T2_out = update_Tinout(G, G, T1, T2, T1_out, T2_out, 5, 5, mapping, reverse_mapping)

    print("fast")
    print(T1)
    print(T2)
    print(T1_out)
    print(T2_out)

    slow_T1, slow_T2, slow_T1_out, slow_T2_out = compute_Ti(G, G, mapping, reverse_mapping)

    print("slow")
    print(slow_T1)
    print(slow_T2)
    print(slow_T1_out)
    print(slow_T2_out)

main()
