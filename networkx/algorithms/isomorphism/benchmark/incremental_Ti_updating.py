import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import (
    feasibility,
    find_candidates,
    initialize_VF2pp,
    VF2pp_solver,
    precheck,
)


def VF2pp(G1, G2, l1, l2):
    try:
        m = next(VF2pp_solver(G1, G2, l1, l2))
        return m
    except StopIteration:
        return None


def VF2pp2(G1, G2, l1, l2):
    try:
        m = next(isomorphic_VF2pp2(G1, G2, l1, l2))
        return m
    except StopIteration:
        return None


def compute_Ti(graph_params, state_params):
    G1, G2, _, _ = graph_params
    mapping, reverse_mapping, T1, T1_out, T2, T2_out = state_params
    T1.clear()
    T1_out.clear()
    T2.clear()
    T2_out.clear()

    T1.update({nbr for node in mapping for nbr in G1[node] if nbr not in mapping})
    T2.update(
        {
            nbr
            for node in reverse_mapping
            for nbr in G2[node]
            if nbr not in reverse_mapping
        }
    )

    T1_out.update({n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1})
    T2_out.update(
        {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}
    )


def isomorphic_VF2pp2(G1, G2, G1_labels, G2_labels):
    if not G1 and not G2:
        return False
    if not precheck(G1, G2, G1_labels, G2_labels):
        return False

    visited = set()
    graph_params, state_params, node_order, stack = initialize_VF2pp(
        G1, G2, G1_labels, G2_labels
    )
    matching_node = 1

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)

            if candidate not in visited and feasibility(
                current_node, candidate, graph_params, state_params
            ):
                visited.add(candidate)
                state_params.mapping.update({current_node: candidate})
                state_params.reverse_mapping.update({candidate: current_node})

                compute_Ti(graph_params, state_params)

                if (
                    len(state_params.mapping) == G1.number_of_nodes()
                ):  # When we match the last node
                    yield state_params.mapping
                    # prepare_next(stack, node_order, visited, state_params)
                    # continue

                next_node = node_order[matching_node]
                matching_node += 1
                candidates = find_candidates(next_node, graph_params, state_params)
                stack.append((next_node, iter(candidates)))

        except StopIteration:
            stack.pop()
            matching_node -= 1
            if (
                stack
            ):  # in the last iteration, it will continue and the while condition will terminate
                popped_node1, _ = stack[-1]
                popped_node2 = state_params.mapping[popped_node1]
                state_params.mapping.pop(popped_node1)
                state_params.reverse_mapping.pop(popped_node2)
                visited.discard(popped_node2)
                compute_Ti(graph_params, state_params)


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
    750,
    800,
]

for V in number_of_nodes:
    print(V)
    G1 = nx.gnp_random_graph(V, 0.7, 42)
    G2 = nx.gnp_random_graph(V, 0.7, 42)

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
    mapping = VF2pp(G1, G2, G1_labels, G2_labels)
    times_incremental.append(time.time() - t0)

    t0 = time.time()
    mapping1 = VF2pp2(G1, G2, G1_labels, G2_labels)
    times_brute_force.append(time.time() - t0)


# plt.plot(number_of_nodes, times_brute_force, label="Brute Force", linestyle="dashed")
# plt.plot(number_of_nodes, times_incremental, label="Incremental")
# plt.xlabel("Number of nodes")
# plt.ylabel("Time seconds")
# plt.legend()
# plt.show()
