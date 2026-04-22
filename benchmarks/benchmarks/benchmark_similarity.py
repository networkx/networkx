"""Benchmarks for graph similarity algorithms."""

import networkx as nx


class GraphEditDistanceBenchmarks:
    timeout = 120
    params = [
        "path_vs_cycle",
        "cycle_vs_wheel",
        "selfloops",
        "directed_cycle",
        "directed_branch",
        "circular_ladder_2_vs_6",
        "multigraph_parallel",
        "multidigraph_small",
    ]
    param_names = ["graph_pair"]

    def setup(self, graph_pair):
        self.graphs = {
            "path_vs_cycle": (nx.path_graph(6), nx.cycle_graph(6)),
            "cycle_vs_wheel": (nx.cycle_graph(6), nx.wheel_graph(7)),
            "selfloops": self.selfloop_graphs(),
            "directed_cycle": self.directed_graphs(),
            "directed_branch": self.directed_branch_graphs(),
            "circular_ladder_2_vs_6": (
                nx.circular_ladder_graph(2),
                nx.circular_ladder_graph(6),
            ),
            "multigraph_parallel": self.multigraph_graphs(),
            "multidigraph_small": self.multidigraph_graphs(),
        }

    def time_graph_edit_distance(self, graph_pair):
        nx.graph_edit_distance(*self.graphs[graph_pair])

    def time_optimize_graph_edit_distance(self, graph_pair):
        for _ in nx.optimize_graph_edit_distance(*self.graphs[graph_pair]):
            pass

    @staticmethod
    def selfloop_graphs():
        G1 = nx.Graph()
        G1.add_edges_from((("A", "A"), ("A", "B")))
        G2 = nx.Graph()
        G2.add_edges_from((("A", "A"), ("A", "B"), ("B", "B")))
        return G1, G2

    @staticmethod
    def directed_graphs():
        G1 = nx.DiGraph()
        G1.add_edges_from((("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")))
        G2 = nx.DiGraph()
        G2.add_edges_from((("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")))
        return G1, G2

    @staticmethod
    def directed_branch_graphs():
        G1 = nx.DiGraph()
        G1.add_edges_from((("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")))
        G2 = nx.DiGraph()
        G2.add_edges_from((("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")))
        return G1, G2

    @staticmethod
    def multigraph_graphs():
        G1 = nx.MultiGraph()
        G1.add_edges_from((("A", "B"), ("B", "C"), ("A", "C")))
        G2 = nx.MultiGraph()
        G2.add_edges_from((("A", "B"), ("B", "C"), ("B", "C"), ("A", "C")))
        return G1, G2

    @staticmethod
    def multidigraph_graphs():
        G1 = nx.MultiDiGraph()
        G1.add_edges_from(
            (
                ("hardware", "kernel"),
                ("kernel", "hardware"),
                ("kernel", "userspace"),
                ("userspace", "kernel"),
            )
        )
        G2 = nx.MultiDiGraph()
        G2.add_edges_from(
            (
                ("winter", "spring"),
                ("spring", "summer"),
                ("summer", "autumn"),
                ("autumn", "winter"),
            )
        )
        return G1, G2


class GraphEditDistanceLabelBenchmarks:
    timeout = 120

    def setup(self):
        self.G1 = nx.Graph()
        self.G1.add_node("A", label="A")
        self.G1.add_node("B", label="B")
        self.G1.add_node("C", label="C")
        self.G1.add_node("D", label="D")
        self.G1.add_edge("A", "B", label="a-b")
        self.G1.add_edge("B", "C", label="b-c")
        self.G1.add_edge("B", "D", label="b-d")

        self.G2 = nx.Graph()
        self.G2.add_node("A", label="A")
        self.G2.add_node("B", label="B")
        self.G2.add_node("D", label="D")
        self.G2.add_node("E", label="E")
        self.G2.add_edge("A", "B", label="a-b")
        self.G2.add_edge("B", "D", label="b-d")
        self.G2.add_edge("D", "E", label="d-e")

    @staticmethod
    def node_match(n1, n2):
        return n1 == n2

    @staticmethod
    def edge_match(e1, e2):
        return e1 == e2

    def time_graph_edit_distance_with_labels(self):
        nx.graph_edit_distance(
            self.G1,
            self.G2,
            node_match=self.node_match,
            edge_match=self.edge_match,
        )

    def time_optimize_graph_edit_distance_with_labels(self):
        for _ in nx.optimize_graph_edit_distance(
            self.G1,
            self.G2,
            node_match=self.node_match,
            edge_match=self.edge_match,
        ):
            pass


class GraphEditDistanceAdvancedBenchmarks:
    timeout = 120

    def setup(self):
        self.rooted_left = nx.star_graph(5)
        self.rooted_right = self.rooted_left.copy()

        self.cost_left = nx.path_graph(6)
        self.cost_right = nx.path_graph(6)
        for node, attr in self.cost_left.nodes.items():
            attr["color"] = "red" if node % 2 == 0 else "blue"
        for node, attr in self.cost_right.nodes.items():
            attr["color"] = "red" if node % 2 == 1 else "blue"

    @staticmethod
    def node_subst_cost(uattr, vattr):
        if uattr["color"] == vattr["color"]:
            return 1
        return 10

    @staticmethod
    def node_del_cost(attr):
        if attr["color"] == "blue":
            return 20
        return 50

    @staticmethod
    def node_ins_cost(attr):
        if attr["color"] == "blue":
            return 40
        return 100

    def time_graph_edit_distance_with_roots(self):
        nx.graph_edit_distance(self.rooted_left, self.rooted_right, roots=(0, 1))

    def time_graph_edit_distance_with_node_costs(self):
        nx.graph_edit_distance(
            self.cost_left,
            self.cost_right,
            node_subst_cost=self.node_subst_cost,
            node_del_cost=self.node_del_cost,
            node_ins_cost=self.node_ins_cost,
        )

    def time_optimize_graph_edit_distance_with_node_costs(self):
        for _ in nx.optimize_graph_edit_distance(
            self.cost_left,
            self.cost_right,
            node_subst_cost=self.node_subst_cost,
            node_del_cost=self.node_del_cost,
            node_ins_cost=self.node_ins_cost,
        ):
            pass
