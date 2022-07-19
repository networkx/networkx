import random
import time
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {
        nbr
        for node in reverse_mapping
        for nbr in G2[node]
        if nbr not in reverse_mapping
    }

    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}
    return T1, T2, T1_out, T2_out


def isomorphic_VF2pp2(G1, G2, G1_labels, G2_labels):
    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())
    visited = set()

    node_order = matching_order(G1, G2, G1_labels, G2_labels)
    starting_node = node_order.pop(0)
    candidates = find_candidates(
        G1, G2, G1_labels, G2_labels, starting_node, mapping, reverse_mapping
    )
    stack = [(starting_node, iter(candidates))]

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
            if (
                feasibility(
                    current_node,
                    candidate,
                    G1,
                    G2,
                    G1_labels,
                    G2_labels,
                    mapping,
                    reverse_mapping,
                    T1,
                    T1_out,
                    T2,
                    T2_out,
                )
                and candidate not in visited
            ):
                visited.add(candidate)

                # Update the mapping and Ti/Ti_out
                mapping.update({current_node: candidate})
                reverse_mapping.update({candidate: current_node})
                T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)
                # Feasibile pair found, extend mapping and descent to the DFS tree searching for another feasible pair
                if not node_order:
                    break

                next_node = node_order.pop(0)
                candidates = find_candidates(
                    G1, G2, G1_labels, G2_labels, next_node, mapping, reverse_mapping
                )
                stack.append((next_node, iter(candidates)))

        except StopIteration:
            # Restore the previous state of the algorithm
            entering_node, _ = stack.pop()  # The node to be returned to the ordering
            node_order.insert(0, entering_node)
            if not stack:
                break

            popped_node1, _ = stack[-1]
            popped_node2 = mapping[popped_node1]
            mapping.pop(popped_node1)
            reverse_mapping.pop(popped_node2)
            visited.remove(popped_node2)  # todo: do we need this?

            T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)

    if len(mapping) == G1.number_of_nodes():
        return mapping
    return False


# Graph initialization
colors = [
    "white",
    "black",
    "green",
    "purple",
    "orange",
    "red",
    "blue",
    "pink",
    "yellow",
    "none",
]
times_brute_force = []
times_incremental = []

number_of_nodes = [
    20,
    50,
    70,
    100,
    130,
    160,
    180,
    210,
    250,
    280,
    310,
    350,
    400,
    450,
    500,
    550,
    600,
    650,
    700,
    750,
    800,
]
for V in number_of_nodes:
    print(V)
    G1 = nx.gnp_random_graph(V, 0.7, 42)
    G2 = nx.gnp_random_graph(V, 0.7, 42)

    # nx.draw(G1, with_labels=True)
    # plt.show()

    # G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
    # G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

    # G1.add_edges_from(G1_edges)
    # G2.add_edges_from(G2_edges)
    # G1.add_node(0)
    # G2.add_node(0)

    # mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

    # for node, color in zip(G1.nodes, colors):
    #     G1.nodes[node]["label"] = color
    #     G2.nodes[mapped_nodes[node]]["label"] = color

    # VF2++ initialization
    for node in G1.nodes():
        color = colors[random.randrange(0, len(colors))]
        G1.nodes[node]["label"] = color
        G2.nodes[node]["label"] = color

    # for n in G1.nodes():
    #     G1.nodes[n]["label"] = "blue"
    #     G2.nodes[n]["label"] = "blue"

    G1_labels = nx.get_node_attributes(G1, "label")
    G2_labels = nx.get_node_attributes(G2, "label")

    # VF2++
    t0 = time.time()
    mapping = isomorphic_VF2pp(G1, G2, G1_labels, G2_labels)
    times_incremental.append(time.time() - t0)

    t0 = time.time()
    mapping1 = isomorphic_VF2pp2(G1, G2, G1_labels, G2_labels)
    times_brute_force.append(time.time() - t0)

    # print(mapping)

plt.plot(number_of_nodes, times_brute_force, label="Brute Force", linestyle="dashed")
plt.plot(number_of_nodes, times_incremental, label="Incremental")
plt.xlabel("Number of nodes")
plt.ylabel("Time seconds")
plt.legend()
plt.show()
