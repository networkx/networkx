import pytest
import networkx as nx


class TestUCS:

    @classmethod
    def setup_class(cls):
        # 2 level tree
        G = nx.Graph()
        G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G'])
        G.add_edges_from([('A', 'B', {'weight': 5}), ('A', 'C', {'weight': 2}),
                          ('D', 'B', {'weight': 9}), ('E', 'B', {'weight': 6}),
                          ('C', 'F', {'weight': 4}), ('C', 'G', {'weight': 10})])

        cls.G = G

    def test_ucs_edges(self):
        edges = nx.ucs_edges(self.G, source='A')
        assert list(edges) == [('A', 'C'), ('A', 'B'), ('C', 'F'),
                               ('B', 'E'), ('C', 'G'), ('B', 'D')]

    def test_ucs_edges_non_existent_source(self):
        with pytest.raises(nx.NodeNotFound) as excinfo:
            list(nx.ucs_edges(self.G, source="idontexist"))
        assert "is not in G" in str(excinfo.value)
