import pytest

import networkx as nx
from networkx.algorithms.traversal.edgedfs import FORWARD, REVERSE


class TestEdgeBFS:
    @classmethod
    def setup_class(cls):
        cls.nodes = [0, 1, 2, 3]
        cls.edges = [(0, 1), (1, 0), (1, 0), (2, 0), (2, 1), (3, 1)]

    def test_empty(self):
        G = nx.Graph()
        edges = list(nx.edge_bfs(G))
        assert edges == []

    def test_empty_orientation_invalid(self):
        G = nx.DiGraph()
        # On an empty digraph, edge_bfs returns empty without checking orientation
        assert list(nx.edge_bfs(G, orientation="invalid")) == []

    def test_graph_single_source(self):
        G = nx.Graph(self.edges)
        G.add_edge(4, 5)
        x = list(nx.edge_bfs(G, [0]))
        x_ = [(0, 1), (0, 2), (1, 2), (1, 3)]
        assert x == x_

    def test_graph(self):
        G = nx.Graph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes))
        x_ = [(0, 1), (0, 2), (1, 2), (1, 3)]
        assert x == x_

    def test_digraph(self):
        G = nx.DiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes))
        x_ = [(0, 1), (1, 0), (2, 0), (2, 1), (3, 1)]
        assert x == x_

    def test_digraph_orientation_invalid(self):
        G = nx.DiGraph(self.edges)
        edge_iterator = nx.edge_bfs(G, self.nodes, orientation="hello")
        pytest.raises(nx.NetworkXError, list, edge_iterator)

    def test_digraph_orientation_none(self):
        G = nx.DiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation=None))
        x_ = [(0, 1), (1, 0), (2, 0), (2, 1), (3, 1)]
        assert x == x_

    def test_digraph_orientation_original(self):
        G = nx.DiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation="original"))
        x_ = [
            (0, 1, FORWARD),
            (1, 0, FORWARD),
            (2, 0, FORWARD),
            (2, 1, FORWARD),
            (3, 1, FORWARD),
        ]
        assert x == x_

    def test_digraph2(self):
        G = nx.DiGraph()
        nx.add_path(G, range(4))
        x = list(nx.edge_bfs(G, [0]))
        x_ = [(0, 1), (1, 2), (2, 3)]
        assert x == x_

    def test_digraph_rev(self):
        G = nx.DiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation="reverse"))
        x_ = [
            (1, 0, REVERSE),
            (2, 0, REVERSE),
            (0, 1, REVERSE),
            (2, 1, REVERSE),
            (3, 1, REVERSE),
        ]
        assert x == x_

    def test_digraph_rev2(self):
        G = nx.DiGraph()
        nx.add_path(G, range(4))
        x = list(nx.edge_bfs(G, [3], orientation="reverse"))
        x_ = [(2, 3, REVERSE), (1, 2, REVERSE), (0, 1, REVERSE)]
        assert x == x_

    def test_multigraph(self):
        G = nx.MultiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes))
        x_ = [(0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 2, 0), (1, 2, 0), (1, 3, 0)]
        # This is an example of where hash randomization can break.
        # There are 3! * 2 alternative outputs, such as:
        #    [(0, 1, 1), (1, 0, 0), (0, 1, 2), (1, 3, 0), (1, 2, 0)]
        # But note, the edges (1,2,0) and (1,3,0) always follow the (0,1,k)
        # edges. So the algorithm only guarantees a partial order. A total
        # order is guaranteed only if the graph data structures are ordered.
        assert x == x_

    def test_multidigraph(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes))
        x_ = [(0, 1, 0), (1, 0, 0), (1, 0, 1), (2, 0, 0), (2, 1, 0), (3, 1, 0)]
        assert x == x_

    def test_multidigraph_rev(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation="reverse"))
        x_ = [
            (1, 0, 0, REVERSE),
            (1, 0, 1, REVERSE),
            (2, 0, 0, REVERSE),
            (0, 1, 0, REVERSE),
            (2, 1, 0, REVERSE),
            (3, 1, 0, REVERSE),
        ]
        assert x == x_

    def test_digraph_ignore(self):
        G = nx.DiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation="ignore"))
        x_ = [
            (0, 1, FORWARD),
            (1, 0, REVERSE),
            (2, 0, REVERSE),
            (2, 1, REVERSE),
            (3, 1, REVERSE),
        ]
        assert x == x_

    def test_digraph_ignore2(self):
        G = nx.DiGraph()
        nx.add_path(G, range(4))
        x = list(nx.edge_bfs(G, [0], orientation="ignore"))
        x_ = [(0, 1, FORWARD), (1, 2, FORWARD), (2, 3, FORWARD)]
        assert x == x_

    def test_multidigraph_ignore(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(nx.edge_bfs(G, self.nodes, orientation="ignore"))
        x_ = [
            (0, 1, 0, FORWARD),
            (1, 0, 0, REVERSE),
            (1, 0, 1, REVERSE),
            (2, 0, 0, REVERSE),
            (2, 1, 0, REVERSE),
            (3, 1, 0, REVERSE),
        ]
        assert x == x_


class TestGenericEdgeBFS:
    def test_empty(self):
        G = nx.Graph()
        assert list(nx.generic_edge_bfs(G)) == []
        assert list(nx.generic_edge_bfs(G, source=None)) == []

    def test_generator_behavior(self):
        G = nx.path_graph(3)
        gen = nx.generic_edge_bfs(G)
        assert iter(gen) is gen
        assert next(gen) == (0, 1)

    def test_path(self):
        G = nx.path_graph(4)
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1), (1, 2), (2, 3)]

    def test_triangle(self):
        G = nx.Graph([(0, 1), (0, 2), (1, 2)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1), (0, 2), (1, 2)]

    def test_cycle(self):
        G = nx.cycle_graph(4)
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1), (0, 3), (1, 2), (3, 2)]

    def test_digraph_cycle(self):
        G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1), (1, 2), (2, 0)]

    def test_digraph_both_directions(self):
        G = nx.DiGraph([(0, 1), (1, 0)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1), (1, 0)]

    def test_multigraph_parallel(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key=0)
        G.add_edge(0, 1, key=1)
        G.add_edge(1, 2, key=0)
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1, 0), (0, 1, 1), (1, 2, 0)]

    def test_multidigraph_parallel(self):
        G = nx.MultiDiGraph()
        G.add_edge(0, 1, key="a")
        G.add_edge(0, 1, key="b")
        G.add_edge(1, 0, key="c")
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1, "a"), (0, 1, "b"), (1, 0, "c")]

    def test_multigraph_data_and_keys(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key="k1", weight=10, meta={"nested": 1})
        G.add_edge(0, 1, key="k2", weight=20, meta={"nested": 2})

        def callback(node):
            return iter(G.edges(node, keys=True, data=True))

        edges = list(nx.generic_edge_bfs(G, source=0, edges=callback))
        assert len(edges) == 2
        assert (0, 1, "k1", {"weight": 10, "meta": {"nested": 1}}) in edges
        assert (0, 1, "k2", {"weight": 20, "meta": {"nested": 2}}) in edges

    def test_multidigraph_data_and_keys(self):
        G = nx.MultiDiGraph()
        G.add_edge(0, 1, key="k1", weight=10, meta={"nested": 1})
        G.add_edge(0, 1, key="k2", weight=20, meta={"nested": 2})

        def callback(node):
            return iter(G.edges(node, keys=True, data=True))

        edges = list(nx.generic_edge_bfs(G, source=0, edges=callback))
        assert len(edges) == 2
        assert (0, 1, "k1", {"weight": 10, "meta": {"nested": 1}}) in edges
        assert (0, 1, "k2", {"weight": 20, "meta": {"nested": 2}}) in edges

    def test_self_loop(self):
        G = nx.Graph([(0, 0), (0, 1)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 0), (0, 1)]

    def test_self_loop_multigraph(self):
        G = nx.MultiGraph([(0, 0, 0), (0, 0, 1)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 0, 0), (0, 0, 1)]

    def test_disconnected_source_none(self):
        G = nx.Graph([(0, 1), (2, 3)])
        edges = list(nx.generic_edge_bfs(G))
        assert edges == [(0, 1), (2, 3)]

    def test_disconnected_single_source(self):
        G = nx.Graph([(0, 1), (2, 3)])
        edges = list(nx.generic_edge_bfs(G, source=0))
        assert edges == [(0, 1)]

    def test_source_none_branch_node_order(self):
        # Graph with branches: 0 - 1 - 2 - 3 and 0 - 4 - 5 - 6
        # Node insertion order dictates queue initialization when source=None
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)])
        expected = [(0, 1), (0, 4), (1, 2), (2, 3), (4, 5), (5, 6)]
        assert list(nx.generic_edge_bfs(G, source=None)) == expected
        assert list(nx.generic_edge_bfs(G)) == expected
        assert list(nx.edge_bfs(G)) == expected

    def test_multiple_sources(self):
        G = nx.Graph([(0, 1), (2, 3), (4, 5)])
        edges = list(nx.generic_edge_bfs(G, source=[0, 2]))
        assert edges == [(0, 1), (2, 3)]

    def test_isolated_nodes(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2])
        assert list(nx.generic_edge_bfs(G)) == []

    def test_custom_filter(self):
        G = nx.Graph()
        G.add_edge(0, 1, weight=1)
        G.add_edge(0, 2, weight=10)
        G.add_edge(1, 2, weight=1)

        def filtered_edges(node):
            for u, v, d in G.edges(node, data=True):
                if d["weight"] < 5:
                    yield (u, v)

        edges = list(nx.generic_edge_bfs(G, source=0, edges=filtered_edges))
        assert edges == [(0, 1), (1, 2)]

    def test_custom_order(self):
        G = nx.star_graph(4)

        def descending_edges(node):
            return sorted(G.edges(node), reverse=True)

        edges = list(nx.generic_edge_bfs(G, source=0, edges=descending_edges))
        assert edges == [(0, 4), (0, 3), (0, 2), (0, 1)]

    def test_empty_callback(self):
        G = nx.path_graph(4)
        edges = list(nx.generic_edge_bfs(G, source=0, edges=lambda n: iter([])))
        assert edges == []

    def test_edge_data_dictionary(self):
        G = nx.path_graph(3)
        G[0][1]["attr"] = {"nested": 1}
        G[1][2]["attr"] = {"nested": 2}

        def data_edges(node):
            return iter(G.edges(node, data=True))

        edges = list(nx.generic_edge_bfs(G, source=0, edges=data_edges))
        assert edges == [
            (0, 1, {"attr": {"nested": 1}}),
            (1, 2, {"attr": {"nested": 2}}),
        ]

    def test_non_incident_edge_raises(self):
        G = nx.path_graph(3)

        def invalid_edges(node):
            if node == 0:
                yield (99, 100)

        with pytest.raises(nx.NetworkXError, match="not incident to parent node"):
            list(nx.generic_edge_bfs(G, source=0, edges=invalid_edges))

    def test_reversed_tuple_incidence(self):
        G = nx.DiGraph([(0, 1), (1, 2)])

        def in_edges(node):
            return iter(G.in_edges(node))

        edges = list(nx.generic_edge_bfs(G, source=2, edges=in_edges))
        assert edges == [(1, 2), (0, 1)]

    def test_matches_edge_bfs(self):
        nodes = [0, 1, 2, 3]
        edges = [(0, 1), (1, 0), (1, 0), (2, 0), (2, 1), (3, 1)]
        for G_cls in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
            G = G_cls(edges)
            assert list(nx.generic_edge_bfs(G, nodes)) == list(nx.edge_bfs(G, nodes))
            assert list(nx.generic_edge_bfs(G, [0])) == list(nx.edge_bfs(G, [0]))
