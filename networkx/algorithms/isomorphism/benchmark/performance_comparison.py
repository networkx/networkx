import time

import matplotlib.pyplot as plt

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import VF2pp


class PerformanceComparison:
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
            G1 = nx.gnp_random_graph(V, p=prob, seed=39)
            G2 = nx.gnp_random_graph(V, p=prob, seed=39)

            for n in G1.nodes():
                G1.nodes[n]["label"] = "blue"
                G2.nodes[n]["label"] = "blue"

            t0 = time.time()
            _ = VF2pp(G1, G2, node_labels="label")
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
            _ = VF2pp(G1, G2, node_labels="label")
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
            _ = VF2pp(G1, G2, node_labels="label")
            dur1 = time.time() - t0

            t0 = time.time()
            _ = nx.is_isomorphic(G1, G2)
            dur2 = time.time() - t0

            self.vf2pp_times.append(dur1)
            self.vf2_times.append(dur2)


if __name__ == "__main__":
    nodes = range(100, 500, 100)
    benchmark = PerformanceComparison(nodes)

    benchmark.compare_in_random_graphs(0.6)
    benchmark.plot_times()
    benchmark.plot_speedup()
