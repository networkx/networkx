import gc
import platform

import pytest

import networkx as nx
from networkx.utils import edges_equal, nodes_equal


class BaseMixedEdgeGraphTester:
    """Tests for data-structure independent graph class features."""

    def test_contains(self):
        G = self.K3
        assert 1 in G
        assert 4 not in G
        assert "b" not in G
        assert [] not in G  # no exception for nonhashable
        assert {1: 1} not in G  # no exception for nonhashable

    def test_order(self):
        G = self.K3
        assert len(G) == 3
        assert G.order() == 3
        assert G.number_of_nodes() == 3

    def test_nodes(self):
        G = self.K3
        assert isinstance(G._node, G.node_dict_factory)
        assert sorted(G.nodes()) == self.k3nodes
        assert sorted(G.nodes(data=True)) == [(0, {}), (1, {}), (2, {})]

    def test_none_node(self):
        G = self.Graph()
        with pytest.raises(ValueError):
            G.add_node(None)
        with pytest.raises(ValueError):
            G.add_nodes_from([None])
        with pytest.raises(ValueError):
            G.add_edge(0, None)
        with pytest.raises(ValueError):
            G.add_edges_from([(0, None)], edge_type="directed")

    def test_has_node(self):
        G = self.K3
        assert G.has_node(1)
        assert not G.has_node(4)
        assert not G.has_node([])  # no exception for nonhashable
        assert not G.has_node({1: 1})  # no exception for nonhashable

    def test_has_edge(self):
        G = self.K3
        assert G.has_edge(0, 1)
        assert not G.has_edge(0, -1)

    def test_neighbors(self):
        G = self.K3
        assert sorted(G.neighbors(0)) == [1, 2]
        with pytest.raises(nx.NetworkXError):
            assert sorted(G.neighbors(-1))

    @pytest.mark.skipif(
        platform.python_implementation() == "PyPy", reason="PyPy gc is different"
    )
    def test_memory_leak(self):
        G = self.Graph()

        def count_objects_of_type(_type):
            return sum(1 for obj in gc.get_objects() if isinstance(obj, _type))

        gc.collect()
        before = count_objects_of_type(self.Graph)
        G.copy()
        gc.collect()
        after = count_objects_of_type(self.Graph)
        assert before == after

        # test a subgraph of the base class
        class MyGraph(self.Graph):
            pass

        gc.collect()
        G = MyGraph()
        before = count_objects_of_type(MyGraph)
        G.copy()
        gc.collect()
        after = count_objects_of_type(MyGraph)
        assert before == after

    def test_size(self):
        G = self.K3
        print(G)
        assert G.size() == 3
        assert G.number_of_edges() == 3

    def test_nbunch_iter(self):
        G = self.K3
        assert nodes_equal(G.nbunch_iter(), self.k3nodes)  # all nodes
        assert nodes_equal(G.nbunch_iter(0), [0])  # single node
        assert nodes_equal(G.nbunch_iter([0, 1]), [0, 1])  # sequence
        # sequence with none in graph
        assert nodes_equal(G.nbunch_iter([-1]), [])
        # string sequence with none in graph
        assert nodes_equal(G.nbunch_iter("foo"), [])
        # node not in graph doesn't get caught upon creation of iterator
        bunch = G.nbunch_iter(-1)
        # but gets caught when iterator used
        with pytest.raises(nx.NetworkXError, match="is not a node or a sequence"):
            list(bunch)
        # unhashable doesn't get caught upon creation of iterator
        bunch = G.nbunch_iter([0, 1, 2, {}])
        # but gets caught when iterator hits the unhashable
        with pytest.raises(
            nx.NetworkXError, match="in sequence nbunch is not a valid node"
        ):
            list(bunch)

    def test_nbunch_iter_node_format_raise(self):
        # Tests that a node that would have failed string formatting
        # doesn't cause an error when attempting to raise a
        # :exc:`nx.NetworkXError`.

        # For more information, see pull request #1813.
        G = self.Graph()
        nbunch = [("x", set())]
        with pytest.raises(nx.NetworkXError):
            list(G.nbunch_iter(nbunch))

    def test_attributes_cached(self):
        G = self.K3.copy()
        assert id(G.nodes) == id(G.nodes)
        assert id(G.adj) == id(G.adj)
        # TODO: not cached property yet
        # assert id(G.edges()) == id(G.edges())
        # assert id(G.degree) == id(G.degree)

    def test_edges(self):
        G = self.K3
        edge_type = self.K3_edge_type
        assert edges_equal(G.edges()[edge_type], [(0, 1), (0, 2), (1, 2)])
        assert edges_equal(G.edges(0)[edge_type], [(0, 1), (0, 2)])
        assert edges_equal(G.edges([0, 1])[edge_type], [(0, 1), (0, 2), (1, 2)])

    def test_degree(self):
        G = self.K3
        assert sorted(G.degree()[self.K3_edge_type]) == [(0, 2), (1, 2), (2, 2)]
        assert dict(G.degree()[self.K3_edge_type]) == {0: 2, 1: 2, 2: 2}
        assert G.degree(0)[self.K3_edge_type] == 2
        with pytest.raises(nx.NetworkXError):
            G.degree(-1)  # node not in graph

    def test_selfloop_degree(self):
        G = self.Graph()
        G.add_edge_type(nx.Graph(), "undirected")
        G.add_edge(1, 1, edge_type="undirected")
        assert sorted(G.degree()[self.K3_edge_type]) == [(1, 2)]
        assert dict(G.degree()[self.K3_edge_type]) == {1: 2}
        assert G.degree(1)[self.K3_edge_type] == 2
        assert sorted(G.degree([1])[self.K3_edge_type]) == [(1, 2)]
        assert G.degree(1, weight="weight")[self.K3_edge_type] == 2

    @pytest.mark.skip(reason="#TODO: doesn't work")
    def test_selfloops(self):
        G = self.K3.copy()
        G.add_edge(0, 0)
        assert nodes_equal(nx.nodes_with_selfloops(G), [0])
        assert edges_equal(nx.selfloop_edges(G), [(0, 0)])
        assert nx.number_of_selfloops(G) == 1
        G.remove_edge(0, 0)
        G.add_edge(0, 0)
        G.remove_edges_from([(0, 0)])
        G.add_edge(1, 1)
        G.remove_node(1)
        G.add_edge(0, 0)
        G.add_edge(1, 1)
        G.remove_nodes_from([0, 1])

    def test_cache_reset(self):
        G = self.K3.copy()
        old_adj = G.adj
        assert id(G.adj) == id(old_adj)
        G.adj = {}
        assert id(G.adj) != id(old_adj)

        old_nodes = G.nodes
        assert id(G.nodes) == id(old_nodes)
        G.nodes = {}
        assert id(G.nodes) != id(old_nodes)


class TestMixedEdgeGraph(BaseMixedEdgeGraphTester):
    def setup_method(self):
        self.Graph = nx.MixedEdgeGraph
        self._graph_func = nx.Graph

        # build dict-of-dict-of-dict K3
        ed1, ed2, ed3 = ({}, {}, {})
        self.k3adj = {0: {1: ed1, 2: ed2}, 1: {0: ed1, 2: ed3}, 2: {0: ed2, 1: ed3}}
        self.k3edges = [(0, 1), (0, 2), (1, 2)]
        self.k3nodes = [0, 1, 2]
        self.K3_edge_type = "undirected"
        self.K3 = self.Graph()
        self.K3.add_edge_type(nx.Graph(), self.K3_edge_type)
        self.K3.add_edges_from(self.k3edges, edge_type=self.K3_edge_type)

    def test_add_edge(self):
        edge_type = "bidirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edge(0, 1, edge_type=edge_type)
        assert G.adj == {edge_type: {0: {1: {}}, 1: {0: {}}}}
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edge(*(0, 1), edge_type=edge_type)
        assert G.adj == {edge_type: {0: {1: {}}, 1: {0: {}}}}

    def test_add_edges_from(self):
        edge_type = "undirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edges_from([(0, 1), (0, 2, {"weight": 3})], edge_type=edge_type)
        assert G.adj[edge_type] == {
            0: {1: {}, 2: {"weight": 3}},
            1: {0: {}},
            2: {0: {"weight": 3}},
        }
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.add_edges_from(
            [(0, 1), (0, 2, {"weight": 3}), (1, 2, {"data": 4})],
            data=2,
            edge_type=edge_type,
        )
        assert G.adj[edge_type] == {
            0: {1: {"data": 2}, 2: {"weight": 3, "data": 2}},
            1: {0: {"data": 2}, 2: {"data": 4}},
            2: {0: {"weight": 3, "data": 2}, 1: {"data": 4}},
        }

        with pytest.raises(nx.NetworkXError):
            G.add_edges_from([(0,)], edge_type=edge_type)  # too few in tuple
        with pytest.raises(nx.NetworkXError):
            G.add_edges_from([(0, 1, 2, 3)], edge_type=edge_type)  # too many in tuple
        with pytest.raises(TypeError):
            G.add_edges_from([0], edge_type=edge_type)  # not a tuple
        with pytest.raises(TypeError):
            G.add_edges_from([0])  # no edge type

    def test_remove_edge(self):
        G = self.K3.copy()
        G.remove_edge(0, 1, self.K3_edge_type)
        assert G.adj == {self.K3_edge_type: {0: {2: {}}, 1: {2: {}}, 2: {0: {}, 1: {}}}}
        with pytest.raises(nx.NetworkXError):
            G.remove_edge(-1, 0, self.K3_edge_type)

    def test_remove_edges_from(self):
        G = self.K3.copy()
        G.remove_edges_from([(0, 1)], self.K3_edge_type)
        assert G.adj == {self.K3_edge_type: {0: {2: {}}, 1: {2: {}}, 2: {0: {}, 1: {}}}}
        G.remove_edges_from([(0, 0)], self.K3_edge_type)  # silent fail

    def test_edges_data(self):
        G = self.K3
        all_edges = [(0, 1, {}), (0, 2, {}), (1, 2, {})]
        assert edges_equal(G.edges(data=True)[self.K3_edge_type], all_edges)
        assert edges_equal(
            G.edges(0, data=True)[self.K3_edge_type], [(0, 1, {}), (0, 2, {})]
        )
        assert edges_equal(G.edges([0, 1], data=True)[self.K3_edge_type], all_edges)
        with pytest.raises(nx.NetworkXError):
            G.edges(-1, True)

    def test_get_edge_data(self):
        G = self.K3.copy()
        assert G.get_edge_data(0, 1) == {self.K3_edge_type: {}}
        assert G[self.K3_edge_type][0][1] == {}
        assert G.get_edge_data(10, 20)[self.K3_edge_type] is None
        assert G.get_edge_data(-1, 0)[self.K3_edge_type] is None
        assert G.get_edge_data(-1, 0, default=1)[self.K3_edge_type] == 1

    def test_update(self):
        # specify both edges and nodes
        G = self.K3.copy()
        G.update(
            nodes=[3, (4, {"size": 2})],
            edges=[(4, 5), (6, 7, {"weight": 2})],
            edge_type=self.K3_edge_type,
        )
        nlist = [
            (0, {}),
            (1, {}),
            (2, {}),
            (3, {}),
            (4, {"size": 2}),
            (5, {}),
            (6, {}),
            (7, {}),
        ]
        assert sorted(G.nodes.data()) == nlist
        if G.is_directed():
            elist = [
                (0, 1, {}),
                (0, 2, {}),
                (1, 0, {}),
                (1, 2, {}),
                (2, 0, {}),
                (2, 1, {}),
                (4, 5, {}),
                (6, 7, {"weight": 2}),
            ]
        else:
            elist = [
                (0, 1, {}),
                (0, 2, {}),
                (1, 2, {}),
                (4, 5, {}),
                (6, 7, {"weight": 2}),
            ]
        assert sorted(G.edges()[self.K3_edge_type].data()) == elist
        assert G.graph == {}

        # no keywords -- order is edges, nodes
        G = self.K3.copy()
        G.update(
            [(4, 5), (6, 7, {"weight": 2})], [3, (4, {"size": 2})], self.K3_edge_type
        )
        assert sorted(G.nodes.data()) == nlist
        assert sorted(G.edges()[self.K3_edge_type].data()) == elist
        assert G.graph == {}

        # TODO: implement updating via another mixed-edge graph
        # update using only a graph
        edge_type = "bidirected"
        G = self.Graph()
        G.add_edge_type(self._graph_func(), edge_type=edge_type)
        G.graph["foo"] = "bar"
        G.add_node(2, data=4)
        G.add_edge(0, 1, edge_type=edge_type, weight=0.5)
        # GG = G.copy()
        # H = self.Graph()
        # H.add_edge_type(self._graph_func(), edge_type=edge_type)
        # GG.update(H)
        # print(G.adj)
        # print(GG.adj)
        # assert graphs_equal(G, GG)
        # H.update(G)
        # assert graphs_equal(H, G)

        # update nodes only
        H = self.Graph()
        with pytest.raises(RuntimeError, match="No edge type"):
            H.update(nodes=[3, 4])
        H.add_edge_type(self._graph_func(), edge_type=edge_type)
        H.update(nodes=[3, 4])
        assert H.nodes ^ {3, 4} == set()
        assert H.size() == 0

        # update edges only
        H = self.Graph()
        with pytest.raises(RuntimeError, match="Edge type is undefined"):
            H.update(edges=[(3, 4)])
        H.add_edge_type(self._graph_func(), edge_type=edge_type)
        H.update(edges=[(3, 4)], edge_type=edge_type)
        assert sorted(H.edges()[edge_type].data()) == [(3, 4, {})]
        assert H.size() == 1

        # No inputs -> exception
        with pytest.raises(nx.NetworkXError):
            nx.Graph().update()
