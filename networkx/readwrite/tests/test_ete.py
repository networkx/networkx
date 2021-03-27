"""
    Unit tests for ete.
"""

import os
import tempfile
import pytest

ete3 = pytest.importorskip("ete3")

import networkx as nx
from networkx.testing import assert_edges_equal, assert_nodes_equal


class TestETE:
    @classmethod
    def setup_class(cls):
        cls.build_graphs()

    @classmethod
    def build_graphs(cls):
        cls.DG = nx.DiGraph(name="test_directed_graph")
        cls.MDG = nx.MultiDiGraph(name="test_multi_graph")

        # Setting nodes with data
        for i in range(0, 42):
            node = str(i)
            cls.DG.add_node(node, data="test_data")
            cls.MDG.add_node(node, data="test_data")

        # Setting edges
        for i in range(1, 42):
            u = str(i - 1)
            v = str(i)

            cls.DG.add_edge(u, v)
            cls.MDG.add_edge(u, v)

    def assert_equal_file_transform(self, G, data=False):
        (fd, fname) = tempfile.mkstemp()
        nx.write_ete(G, fname)
        Gin = nx.read_ete(fname)

        assert nx.is_arborescence(G)
        assert nx.is_arborescence(Gin)

        assert_nodes_equal(list(G), list(Gin))
        assert_edges_equal(G.edges(data=data), Gin.edges(data=data))

        os.close(fd)
        os.unlink(fname)

    def assert_equal_instance_transform(self, G, data=False):
        T = nx.to_ete(G)
        Gin = nx.from_ete(T)

        assert nx.is_arborescence(G)
        assert nx.is_arborescence(Gin)

        assert_nodes_equal(list(G), list(Gin))
        assert_edges_equal(G.edges(data=data), Gin.edges(data=data))

    def test_directed_through_file_transformation(self):
        self.assert_equal_file_transform(self.DG, data=True)

    def test_multigraph_through_file_transformation(self):
        self.assert_equal_file_transform(self.MDG, data=True)

    def test_directed_through_instance_transformation(self):
        self.assert_equal_instance_transform(self.DG, data=True)

    def test_multigraph_through_instance_transformation(self):
        self.assert_equal_instance_transform(self.MDG, data=True)
