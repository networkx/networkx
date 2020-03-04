"""
Unit tests for dedensification/densification
"""

import networkx as nx
from networkx.algorithms.dedensification import dedensify, densify


class TestDirectedDedensification:

    def build_original_graph(self):
        original_matrix = [
            ('1', 'BC'),
            ('2', 'ABC'),
            ('3', ['A', 'B', '6']),
            ('4', 'ABC'),
            ('5', 'AB'),
            ('6', ['5']),
            ('A', ['6']),
        ]
        graph = nx.DiGraph()
        for source, targets in original_matrix:
            for target in targets:
                graph.add_edge(source, target)
        return graph

    def build_compressed_graph(self):
        compressed_matrix = [
            ('1', ['BC']),
            ('2', ['ABC']),
            ('3', ['AB', '6']),
            ('4', ['ABC']),
            ('5', ['AB']),
            ('6', ['5']),
            ('A', ['6']),
            ('ABC', 'ABC'),
            ('AB', 'AB'),
            ('BC', 'BC')
        ]
        compressed_graph = nx.DiGraph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_empty(self):
        G = nx.Graph()
        compressed_graph, c_nodes = dedensify(G, expansive=True, prefix='C-')
        assert c_nodes == set()


class TestDirectedExpansiveDedensification(TestDirectedDedensification):

    def setup_method(self):
        self.c_nodes = ('AB', 'BC', 'ABC')

    def test_dedensify_edges(self):
        G = self.build_original_graph()
        compressed_G = self.build_compressed_graph()
        compressed_graph, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=True,
            inplace=True
        )
        for s, t in compressed_graph.edges():
            o_s = ''.join(sorted(s))
            o_t = ''.join(sorted(t))
            compressed_graph_edge_exists = compressed_graph.has_edge(s, t)
            verified_compressed_edge_exists = compressed_G.has_edge(o_s, o_t)
            assert compressed_graph_edge_exists == verified_compressed_edge_exists
        assert len(c_nodes) == len(self.c_nodes)

    def test_densify_edges(self):
        original_graph = self.build_original_graph()
        compressed_G = self.build_compressed_graph()
        G = densify(compressed_G, self.c_nodes, inplace=True)
        for s, t in original_graph.edges():
            assert original_graph.has_edge(s, t) == G.has_edge(s, t)


class TestDirectedNonExpansiveDedensification(TestDirectedDedensification):

    def setup_method(self):
        print('setup_method TestDirectedNonExpansiveDedensification')
        self.c_nodes = ('ABC', )

    def build_compressed_graph(self):
        compressed_matrix = [
            ('1', 'BC'),
            ('2', ['ABC']),
            ('3', ['A', 'B', '6']),
            ('4', ['ABC']),
            ('5', 'AB'),
            ('6', ['5']),
            ('A', ['6']),
            ('ABC', 'ABC')
        ]
        compressed_graph = nx.DiGraph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_dedensify_edges(self):
        G = self.build_original_graph()
        compressed_G = self.build_compressed_graph()
        compressed_graph, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=False,
        )
        for s, t in compressed_graph.edges():
            o_s = ''.join(sorted(s))
            o_t = ''.join(sorted(t))
            compressed_graph_edge_exists = compressed_graph.has_edge(s, t)
            print(o_s, o_t)
            verified_compressed_edge_exists = compressed_G.has_edge(o_s, o_t)
            assert compressed_graph_edge_exists == verified_compressed_edge_exists
        assert len(c_nodes) == len(self.c_nodes)

    def test_dedensify_edge_count(self):
        G = self.build_original_graph()
        original_edge_count = len(G.edges())
        compressed_G, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=False,
            inplace=True
        )
        compressed_edge_count = len(compressed_G.edges())
        assert compressed_edge_count <= original_edge_count
        compressed_G = self.build_compressed_graph()
        assert compressed_edge_count == len(compressed_G.edges())

    def test_densify_edges(self):
        compressed_G = self.build_compressed_graph()
        original_graph = densify(compressed_G, self.c_nodes, inplace=True)
        G = self.build_original_graph()
        for s, t in G.edges():
            assert G.has_edge(s, t) == original_graph.has_edge(s, t)

    def test_densify_edge_count(self):
        compressed_G = self.build_compressed_graph()
        compressed_edge_count = len(compressed_G.edges())
        original_graph = densify(compressed_G, self.c_nodes, inplace=True)
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
            ('1', 'CB'),
            ('2', 'ABC'),
            ('3', ['A', 'B', '6']),
            ('4', 'ABC'),
            ('5', 'AB'),
            ('6', ['5']),
            ('A', ['6']),
        ]
        graph = nx.Graph()
        for source, targets in original_matrix:
            for target in targets:
                graph.add_edge(source, target)
        return graph

    def test_empty(self):
        G = nx.Graph()
        compressed_G, c_nodes = dedensify(G, expansive=True, prefix='C-')
        assert c_nodes == set()


class TestUnDirectedExpansiveDedensification(TestUnDirectedDedensification):

    def setup_method(self):
        self.c_nodes = ('BC', 'ABC', '35A', '24', '23456', '2345', '6AB')

    def build_compressed_graph(self):
        compressed_matrix = [
            ('1', ['BC']),
            ('2', ['24', '2345', '23456', 'ABC']),
            ('3', ['35A', '2345', '23456', '6AB']),
            ('4', ['24', '2345', '23456', 'ABC']),
            ('5', ['2345', '23456', '35A', '6AB']),
            ('6', ['35A', '6AB', '23456']),
            ('A', ['23456', '35A', 'ABC', '6AB']),
            ('B', ['BC', '2345', '6AB', 'ABC']),
            ('C', ['24', 'BC', 'ABC']),
        ]
        compressed_graph = nx.Graph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_dedensify_edges(self):
        G = self.build_original_graph()
        v_compressed_G = self.build_compressed_graph()
        compressed_G, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=True,
            inplace=True
        )
        for s, t in compressed_G.edges():
            o_s = ''.join(sorted(s))
            o_t = ''.join(sorted(t))
            assert compressed_G.has_edge(s, t) == v_compressed_G.has_edge(o_s, o_t)
        assert len(c_nodes) == len(self.c_nodes)

    def test_dedensify_edge_count(self):
        G = self.build_original_graph()
        verified_compressed_G = self.build_compressed_graph()
        compressed_G, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=True,
            inplace=True
        )
        compressed_edge_count = len(compressed_G.edges())
        verified_compressed_edge_count = len(verified_compressed_G.edges())
        assert compressed_edge_count == verified_compressed_edge_count


class TestUnDirectedNonExpansiveDedensification(TestUnDirectedDedensification):

    def setup_method(self):
        self.c_nodes = ('6AB', 'ABC', )

    def build_compressed_graph(self):
        compressed_matrix = [
            ('1', ['B', 'C']),
            ('2', ['ABC']),
            ('3', ['6AB']),
            ('4', ['ABC']),
            ('5', ['6AB']),
            ('6', ['6AB', 'A']),
            ('A', ['6AB', 'ABC']),
            ('B', ['ABC', '6AB']),
            ('C', ['ABC'])
        ]
        compressed_graph = nx.Graph()
        for source, targets in compressed_matrix:
            for target in targets:
                compressed_graph.add_edge(source, target)
        return compressed_graph

    def test_dedensify_edges(self):
        G = self.build_original_graph()
        compressed_G, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=False,
            inplace=True
        )
        v_compressed_G = self.build_compressed_graph()
        for s, t in compressed_G.edges():
            o_s = ''.join(sorted(s))
            o_t = ''.join(sorted(t))
            assert compressed_G.has_edge(s, t) == v_compressed_G.has_edge(o_s, o_t)
        assert len(c_nodes) == len(self.c_nodes)

    def test_dedensify_edge_count(self):
        G = self.build_original_graph()
        compressed_G, c_nodes = dedensify(
            G,
            threshold=2,
            expansive=False,
            inplace=True
        )
        compressed_edge_count = len(compressed_G.edges())
        verified_original_edge_count = len(G.edges())
        assert compressed_edge_count <= verified_original_edge_count
        verified_compressed_G = self.build_compressed_graph()
        verified_compressed_edge_count = len(verified_compressed_G.edges())
        assert compressed_edge_count == verified_compressed_edge_count
