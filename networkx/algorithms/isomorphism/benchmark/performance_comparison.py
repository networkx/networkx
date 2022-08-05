import collections
import time

import matplotlib.pyplot as plt

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import (
    vf2pp_is_isomorphic,
    _feasibility,
    _matching_order,
    _precheck,
    _restore_state,
)
from networkx.algorithms.isomorphism.vf2pp_helpers.state import _update_Tinout


class VF2VF2ppComparison:
    def __init__(self, number_of_nodes):
        self.number_of_nodes = number_of_nodes
        self.vf2_times = []
        self.vf2pp_times = []

    def reset(self):
        self.vf2pp_times.clear()
        self.vf2_times.clear()

    def plot_times(self):
        plt.plot(self.number_of_nodes, self.vf2_times, label="vf2", linestyle="dashed")
        plt.plot(self.number_of_nodes, self.vf2pp_times, label="vf2++")
        plt.xlabel(xlabel="number of nodes")
        plt.ylabel(ylabel="time (second)")
        plt.legend()
        plt.show()

    def plot_speedup(self):
        speedup = [slow / fast for slow, fast in zip(self.vf2_times, self.vf2pp_times)]
        plt.plot(self.number_of_nodes, speedup)
        plt.xlabel(xlabel="number of nodes")
        plt.ylabel(ylabel="speedup (t_vf2 / t_vf2pp)")
        plt.legend()
        plt.show()

    def compare_in_random_graphs(self, prob=0.5):
        for V in self.number_of_nodes:
            print(f"V = {V}")
            G1 = nx.gnp_random_graph(V, p=prob, seed=39)
            G2 = nx.gnp_random_graph(V, p=prob, seed=39)

            for n in G1.nodes():
                G1.nodes[n]["label"] = "blue"
                G2.nodes[n]["label"] = "blue"

            t0 = time.time()
            _ = vf2pp_is_isomorphic(G1, G2, node_labels="label")
            dur1 = time.time() - t0

            t0 = time.time()
            _ = nx.is_isomorphic(G1, G2)
            dur2 = time.time() - t0

            self.vf2pp_times.append(dur1)
            self.vf2_times.append(dur2)

    def compare_in_disconnected_graphs(self):
        for V in self.number_of_nodes:
            G1 = nx.Graph()
            G2 = nx.Graph()
            G1.add_nodes_from([node for node in range(V)])
            G2.add_nodes_from([node for node in range(V)])

            for n in G1.nodes():
                G1.nodes[n]["label"] = "blue"
                G2.nodes[n]["label"] = "blue"

            t0 = time.time()
            _ = vf2pp_is_isomorphic(G1, G2, node_labels="label")
            dur1 = time.time() - t0

            t0 = time.time()
            _ = nx.is_isomorphic(G1, G2)
            dur2 = time.time() - t0

            self.vf2pp_times.append(dur1)
            self.vf2_times.append(dur2)

    def compare_in_complete_graphs(self):
        for V in self.number_of_nodes:
            G1 = nx.complete_graph(V)
            G2 = nx.complete_graph(V)

            for n in G1.nodes():
                G1.nodes[n]["label"] = "blue"
                G2.nodes[n]["label"] = "blue"

            t0 = time.time()
            _ = vf2pp_is_isomorphic(G1, G2, node_labels="label")
            dur1 = time.time() - t0

            t0 = time.time()
            _ = nx.is_isomorphic(G1, G2)
            dur2 = time.time() - t0

            self.vf2pp_times.append(dur1)
            self.vf2_times.append(dur2)


class CandidateSelectionMethodComparison:
    def __init__(self, number_of_nodes):
        self.number_of_nodes = number_of_nodes
        self.default_candidates_times = []
        self.optimized_candidates_times = []

    def plot_times(self):
        plt.plot(
            self.number_of_nodes,
            self.default_candidates_times,
            label="Default candidates calculation",
            linestyle="dashed",
        )
        plt.plot(
            self.number_of_nodes,
            self.optimized_candidates_times,
            label="Optimized candidates calculation",
        )
        plt.xlabel(xlabel="number of nodes")
        plt.ylabel(ylabel="time (second)")
        plt.legend()
        plt.show()

    def plot_speedup(self):
        speedup = [
            slow / fast
            for slow, fast in zip(
                self.default_candidates_times, self.optimized_candidates_times
            )
        ]
        plt.plot(self.number_of_nodes, speedup)
        plt.xlabel(xlabel="number of nodes")
        plt.ylabel(ylabel="speedup (t_default / t_optimized)")
        plt.legend()
        plt.show()

    def reset(self):
        self.default_candidates_times.clear()
        self.optimized_candidates_times.clear()

    def compare_in_random_graphs(self, prob=0.5):
        for V in self.number_of_nodes:
            G1 = nx.gnp_random_graph(V, p=prob, seed=39)
            G2 = nx.gnp_random_graph(V, p=prob, seed=39)

            for n in G1.nodes():
                G1.nodes[n]["label"] = "blue"
                G2.nodes[n]["label"] = "blue"

            l1, l2 = nx.get_node_attributes(G1, "label"), nx.get_node_attributes(
                G2, "label"
            )

            t0 = time.time()
            _ = vf2pp_is_isomorphic(G1, G2, node_labels="label")
            dur1 = time.time() - t0

            t0 = time.time()
            _ = VF2pp_default_candidates(G1, G2, l1, l2)
            dur2 = time.time() - t0

            self.optimized_candidates_times.append(dur1)
            self.default_candidates_times.append(dur2)


def VF2pp_default_candidates(G1, G2, G1_labels, G2_labels):
    try:
        mapping = next(VF2pp_solver_default_candidates(G1, G2, G1_labels, G2_labels))
        return mapping
    except StopIteration:
        return None


def VF2pp_solver_default_candidates(G1, G2, G1_labels, G2_labels):
    if not G1 and not G2:
        return False
    if not _precheck(G1, G2, G1_labels, G2_labels):
        return False

    graph_params, state_params, node_order, stack = initialize_VF2pp_default_candidates(
        G1, G2, G1_labels, G2_labels
    )
    matching_node = 1
    mapping = state_params.mapping

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
        except StopIteration:
            stack.pop()
            matching_node -= 1
            if stack:
                _restore_state(stack, graph_params, state_params)
            continue

        if _feasibility(current_node, candidate, graph_params, state_params):
            if len(mapping) == G2.number_of_nodes() - 1:
                mapping.update({current_node: candidate})
                yield state_params.mapping

            update_state_default_candidates(
                current_node,
                candidate,
                matching_node,
                node_order,
                stack,
                graph_params,
                state_params,
            )
            matching_node += 1


def find_default_candidates(graph_params, state_params):
    G1, G2, G1_labels, _, _, nodes_of_G2Labels, G2_nodes_of_degree = graph_params
    mapping, reverse_mapping, T1, _, T2, _ = state_params

    if T1 and T2:
        return {node for node in T2}
    return {node for node in G2.nodes() if node not in reverse_mapping}


def initialize_VF2pp_default_candidates(G1, G2, G1_labels, G2_labels):
    GraphParameters = collections.namedtuple(
        "GraphParameters",
        [
            "G1",
            "G2",
            "G1_labels",
            "G2_labels",
            "nodes_of_G1Labels",
            "nodes_of_G2Labels",
            "G2_nodes_of_degree",
        ],
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    graph_params = GraphParameters(
        G1,
        G2,
        G1_labels,
        G2_labels,
        nx.utils.groups(G1_labels),
        nx.utils.groups(G2_labels),
        nx.utils.groups({node: degree for node, degree in G2.degree()}),
    )
    state_params = StateParameters(
        dict(), dict(), set(), set(G1.nodes()), set(), set(G2.nodes())
    )

    node_order = _matching_order(graph_params)

    starting_node = node_order[0]
    candidates = find_default_candidates(graph_params, state_params)
    stack = [(starting_node, iter(candidates))]

    return graph_params, state_params, node_order, stack


def update_state_default_candidates(
    node, candidate, matching_node, order, stack, graph_params, state_params
):
    state_params.mapping.update({node: candidate})
    state_params.reverse_mapping.update({candidate: node})
    _update_Tinout(node, candidate, graph_params, state_params)

    next_node = order[matching_node]
    candidates = find_default_candidates(graph_params, state_params)
    stack.append((next_node, iter(candidates)))
