"""
Unit tests for dedensification/densification
"""

import networkx as nx
from networkx.algorithms.summarization import dedensify


class TestDirectedDedensification:
    def build_original_graph(self):
        original_matrix = [
            ("1", "BC"),
            ("2", "ABC"),
            ("3", ["A", "B", "6"]),
            ("4", "ABC"),
            ("5", "AB"),
            ("6", ["5"]),
            ("A", ["6"]),
        ]
        graph = nx.DiGraph()
        for source, targets in original_matrix:
            for target in targets:
                graph.add_edge(source, target)
        return graph

    def build_compressed_graph(self):
        compressed_matrix = [
            ("1", "BC"),
            ("2", ["ABC"]),
            ("3", ["A", "B", "6"]),
            ("4", ["ABC"]),
            ("5", "AB"),
            ("6", ["5"]),
            ("A", ["6"]),
            ("ABC", "ABC"),
        ]
        compressed_graph = nx.DiGraph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_empty(self):
        """
        Verify that an empty directed graph results in no compressor nodes
        """
        G = nx.DiGraph()
        compressed_graph, c_nodes = dedensify(G, threshold=2)
        assert c_nodes == set()

    @staticmethod
    def densify(G, compressor_nodes, copy=True):
        """
        Reconstructs the original graph from a dedensified, directed graph

        Parameters
        ----------
        G: dedensified graph
           A networkx graph
        compressor_nodes: iterable
           Iterable of compressor nodes in the dedensified graph
        inplace: bool, optional (default: False)
           Indicates if densification should be done inplace

        Returns
        -------
        G: graph
           A densified networkx graph
        """
        if copy:
            G = G.copy()
        for compressor_node in compressor_nodes:
            all_neighbors = set(nx.all_neighbors(G, compressor_node))
            out_neighbors = set(G.neighbors(compressor_node))
            for out_neighbor in out_neighbors:
                G.remove_edge(compressor_node, out_neighbor)
            in_neighbors = all_neighbors - out_neighbors
            for in_neighbor in in_neighbors:
                G.remove_edge(in_neighbor, compressor_node)
                for out_neighbor in out_neighbors:
                    G.add_edge(in_neighbor, out_neighbor)
            G.remove_node(compressor_node)
        return G

    def setup_method(self):
        self.c_nodes = ("ABC",)

    def test_dedensify_edges(self):
        """
        Verifies that dedensify produced the correct edges to/from compressor
        nodes in a directed graph
        """
        G = self.build_original_graph()
        compressed_G = self.build_compressed_graph()
        compressed_graph, c_nodes = dedensify(G, threshold=2)
        for s, t in compressed_graph.edges():
            o_s = "".join(sorted(s))
            o_t = "".join(sorted(t))
            compressed_graph_exists = compressed_graph.has_edge(s, t)
            verified_compressed_exists = compressed_G.has_edge(o_s, o_t)
            assert compressed_graph_exists == verified_compressed_exists
        assert len(c_nodes) == len(self.c_nodes)

    def test_dedensify_edge_count(self):
        """
        Verifies that dedensify produced the correct number of comrpessor nodes
        in a directed graph
        """
        G = self.build_original_graph()
        original_edge_count = len(G.edges())
        c_G, c_nodes = dedensify(G, threshold=2)
        compressed_edge_count = len(c_G.edges())
        assert compressed_edge_count <= original_edge_count
        compressed_G = self.build_compressed_graph()
        assert compressed_edge_count == len(compressed_G.edges())

    def test_densify_edges(self):
        """
        Verifies that densification produces the correct edges from the
        original directed graph
        """
        compressed_G = self.build_compressed_graph()
        original_graph = self.densify(compressed_G, self.c_nodes, copy=True)
        G = self.build_original_graph()
        for s, t in G.edges():
            assert G.has_edge(s, t) == original_graph.has_edge(s, t)

    def test_densify_edge_count(self):
        """
        Verifies that densification produces the correct number of edges in the
        original directed graph
        """
        compressed_G = self.build_compressed_graph()
        compressed_edge_count = len(compressed_G.edges())
        original_graph = self.densify(compressed_G, self.c_nodes)
        original_edge_count = len(original_graph.edges())
        assert compressed_edge_count <= original_edge_count
        G = self.build_original_graph()
        assert original_edge_count == len(G.edges())


class TestUnDirectedDedensification:
    def build_original_graph(self):
        """
        Builds graph shown in the original research paper
        """
        original_matrix = [
            ("1", "CB"),
            ("2", "ABC"),
            ("3", ["A", "B", "6"]),
            ("4", "ABC"),
            ("5", "AB"),
            ("6", ["5"]),
            ("A", ["6"]),
        ]
        graph = nx.Graph()
        for source, targets in original_matrix:
            for target in targets:
                graph.add_edge(source, target)
        return graph

    def test_empty(self):
        """
        Verify that an empty undirected graph results in no compressor nodes
        """
        G = nx.Graph()
        compressed_G, c_nodes = dedensify(G, threshold=2)
        assert c_nodes == set()

    def setup_method(self):
        self.c_nodes = (
            "6AB",
            "ABC",
        )

    def build_compressed_graph(self):
        compressed_matrix = [
            ("1", ["B", "C"]),
            ("2", ["ABC"]),
            ("3", ["6AB"]),
            ("4", ["ABC"]),
            ("5", ["6AB"]),
            ("6", ["6AB", "A"]),
            ("A", ["6AB", "ABC"]),
            ("B", ["ABC", "6AB"]),
            ("C", ["ABC"]),
        ]
        compressed_graph = nx.Graph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_dedensify_edges(self):
        """
        Verifies that dedensify produced correct compressor nodes and the
        correct edges to/from the compressor nodes in an undirected graph
        """
        G = self.build_original_graph()
        c_G, c_nodes = dedensify(G, threshold=2)
        v_compressed_G = self.build_compressed_graph()
        for s, t in c_G.edges():
            o_s = "".join(sorted(s))
            o_t = "".join(sorted(t))
            has_compressed_edge = c_G.has_edge(s, t)
            verified_has_compressed_edge = v_compressed_G.has_edge(o_s, o_t)
            assert has_compressed_edge == verified_has_compressed_edge
        assert len(c_nodes) == len(self.c_nodes)

    def test_dedensify_edge_count(self):
        """
        Verifies that dedensify produced the correct number of edges in an
        undirected graph
        """
        G = self.build_original_graph()
        c_G, c_nodes = dedensify(G, threshold=2, copy=True)
        compressed_edge_count = len(c_G.edges())
        verified_original_edge_count = len(G.edges())
        assert compressed_edge_count <= verified_original_edge_count
        verified_compressed_G = self.build_compressed_graph()
        verified_compressed_edge_count = len(verified_compressed_G.edges())
        assert compressed_edge_count == verified_compressed_edge_count
