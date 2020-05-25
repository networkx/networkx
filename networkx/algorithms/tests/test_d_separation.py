from itertools import combinations
import pytest
import networkx as nx


class TestDSeparation:
    @classmethod
    def setup_class(cls):
        cls.path_G = nx.path_graph(3, create_using=nx.DiGraph)
        cls.path_G.graph["name"] = "path"
        nx.freeze(cls.path_G)

        cls.fork_G = nx.DiGraph(name="fork")
        cls.fork_G.add_edges_from([(0, 1), (0, 2)])
        nx.freeze(cls.fork_G)

        cls.collider_G = nx.DiGraph(name="collider")
        cls.collider_G.add_edges_from([(0, 2), (1, 2)])
        nx.freeze(cls.collider_G)

        cls.naive_bayes_G = nx.DiGraph(name="naive_bayes")
        cls.naive_bayes_G.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4)])
        nx.freeze(cls.naive_bayes_G)

        cls.asia_G = nx.DiGraph(name="asia")
        cls.asia_G.add_edges_from([('asia', 'tuberculosis'),
                                   ('smoking', 'cancer'),
                                   ('smoking', 'bronchitis'),
                                   ('tuberculosis', 'either'),
                                   ('cancer', 'either'), ('either', 'xray'),
                                   ('either', 'dyspnea'),
                                   ('bronchitis', 'dyspnea')])
        nx.freeze(cls.asia_G)

        cls.graphs = [
            cls.path_G, cls.fork_G, cls.collider_G, cls.naive_bayes_G,
            cls.asia_G
        ]

    def test_markov_condition(self):
        for graph in self.graphs:
            for node in graph.nodes:
                parents = set(graph.predecessors(node))
                non_descendants = graph.nodes - nx.descendants(
                    graph, node) - {node} - parents
                assert nx.d_separated(graph, {node}, non_descendants, parents)

    def test_d_separation_examples(self):
        assert nx.d_separated(self.path_G, {0}, {2}, {1})
        assert not nx.d_separated(self.path_G, {0}, {2}, {})

        assert nx.d_separated(self.fork_G, {1}, {2}, {0})
        assert not nx.d_separated(self.fork_G, {1}, {2}, {})

        assert nx.d_separated(self.collider_G, {0}, {1}, {})
        assert not nx.d_separated(self.collider_G, {0}, {1}, {2})

        for u, v in combinations(range(1, 5), 2):
            assert nx.d_separated(self.naive_bayes_G, {u}, {v}, {0})
            assert not nx.d_separated(self.naive_bayes_G, {u}, {v}, {})

        assert nx.d_separated(self.asia_G, {'asia', 'smoking'},
                              {'dyspnea', 'xray'}, {'bronchitis', 'either'})
        assert nx.d_separated(self.asia_G, {'tuberculosis', 'cancer'},
                              {'bronchitis'}, {'smoking', 'xray'})

    def test_undirected_graphs_are_not_supported(self):
        with pytest.raises(nx.NetworkXNotImplemented):
            g = nx.path_graph(3, nx.Graph)
            nx.d_separated(g, {0}, {1}, {2})

    def test_cyclic_graphs_raise_error(self):
        with pytest.raises(nx.NetworkXError):
            g = nx.cycle_graph(3, nx.DiGraph)
            nx.d_separated(g, {0}, {1}, {2})

    def test_invalid_nodes_raise_error(self):
        with pytest.raises(nx.NodeNotFound):
            nx.d_separated(self.asia_G, {0}, {1}, {2})
