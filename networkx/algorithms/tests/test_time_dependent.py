"""Unit testing for time dependent algorithms."""

import pytest
import networkx as nx
from datetime import datetime

class TestCdIndex:

    def test_datetime(self):
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        G.add_edge(1, 4)
        G.add_edge(1, 5)
        G.add_edge(6, 1)
        G.add_edge(7, 1)
        G.add_edge(8, 1)
        G.add_edge(9, 1)
        G.add_edge(10, 1)
        G.add_edge(11, 1)

        node_attrs = {
            1: {'time': datetime(2022, 1, 1)},
            2: {'time': datetime(2022, 1, 1)},
            3: {'time': datetime(2022, 1, 1)},
            4: {'time': datetime(2022, 1, 1)},
            5: {'time': datetime(2022, 1, 1)},
            6: {'time': datetime(2022, 1, 1)},
            7: {'time': datetime(2022, 1, 1)},
            8: {'time': datetime(2022, 1, 1)},
            9: {'time': datetime(2022, 1, 1)},
            10: {'time': datetime(2022,1, 1)},
            11: {'time': datetime(2022, 4, 1)}
        }

        # Set the node attributes for the graph
        nx.set_node_attributes(G, node_attrs)

        print(G.nodes.data('time'))

        assert nx.cd_index(G, 1, datetime(2022,4, 1)) == 1

    def test_extra_nodes(self):
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        G.add_edge(4, 1)
        G.add_edge(5, 1)
        G.add_edge(6, 2)
        G.add_edge(7, 4)

        assert nx.cd_index(G, 1) == 0.67