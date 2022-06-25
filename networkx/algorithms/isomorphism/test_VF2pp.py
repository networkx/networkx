import collections
import random
import runpy
import time

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def main():
    G = nx.gnp_random_graph(2000, 0.35, seed=42)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]

    for i in range(len(G.nodes)):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    G1_labels = {n: G.nodes[n]["label"] for n in G.nodes()}
    G2_labels = G1_labels

    # pos = graphviz_layout(G, prog='dot')
    # nx.draw(G, pos, with_labels=True, arrows=False)
    # plt.show()

    m = {node: node for node in G.nodes() if node < G.number_of_nodes() // 4}
    s = State(G1=G, G2=G, u=1999, node_order=None, mapping=m, reverse_mapping=m)

    cnt = 0
    feasible = -1
    for n in G.nodes():
        if check_feasibility(node1=0, node2=n, G1=G, G2=G, G1_labels=G1_labels, G2_labels=G2_labels, state=s):
            feasible = n
            cnt += 1

    print("Number of feasible nodes: ", cnt)
    print("feasible node: ", feasible)

    # for i in range(20):
    #     print(prune_ISO(G, G, 5, i, s))
    #     print(prune_IND(G, G, 5, i, s))


class State:
    def __init__(self, G1, G2, u, node_order, mapping, reverse_mapping):
        self.u = u
        self.node_order = node_order
        self.mapping = mapping
        self.reverse_mapping = reverse_mapping

        # todo: store T1 and T2 in the state.
        # todo: should we keep the reverse mapping, instead of using values?
        self.T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
        self.T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}

        self.T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in self.T1}
        self.T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in self.T2}


def check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, state):
    # todo: add IND, SUB cases as well
    if G1_labels[node1] != G2_labels[node2]:
        return False

    if G1.number_of_edges(node1, node1) != G2.number_of_edges(node2, node2):
        return False

    if prune_ISO(G1, G2, node1, node2, state):
        return False
    # Check if every covered neighbor of u is mapped to every covered neighbor of v
    # Also check if there is the same number of edges between the candidates and their neighbors
    for neighbor in G1[node1]:
        if neighbor in state.mapping:
            if state.mapping[neighbor] not in G2[node2]:
                return False
            elif G1.number_of_edges(node1, neighbor) != G2.number_of_edges(node2, state.mapping[neighbor]):
                return False
            elif G1_labels[neighbor] != G2_labels[state.mapping[neighbor]]:
                return False

    for neighbor in G2[node2]:
        if neighbor in state.reverse_mapping:
            if state.reverse_mapping[neighbor] not in G1[node1]:
                return False
            elif G1.number_of_edges(node1, state.reverse_mapping[neighbor]) != G2.number_of_edges(node2, neighbor):
                return False
            elif G1_labels[state.reverse_mapping[neighbor]] != G2_labels[neighbor]:
                return False
    return True


def prune_ISO(G1, G2, u, v, state):
    u_neighbors_labels = {n1: G1.nodes[n1]["label"] for n1 in G1[u]}
    u_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(u_neighbors_labels).items()))

    v_neighbors_labels = {n2: G2.nodes[n2]["label"] for n2 in G2[v]}
    v_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(v_neighbors_labels).items()))
    # if the neighbors of u, do not have the same labels as those of v, feasibility cannot be established.
    if set(u_labels_neighbors.keys()) != set(v_labels_neighbors.keys()):
        return True

    for nh1, nh2 in zip(u_labels_neighbors.values(), v_labels_neighbors.values()):
        if len(state.T1.intersection(nh1)) != len(state.T2.intersection(nh2)) or \
                len(state.T1_out.intersection(nh1)) != len(state.T2_out.intersection(nh2)):
            return True

    return False


main()
