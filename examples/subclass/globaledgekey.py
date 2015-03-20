"""
A subclass of the MultiDiGraph class which uses a global edge key.

"""
from __future__ import print_function

from collections import OrderedDict
import networkx as nx

class MultiDiGraph(nx.MultiDiGraph):
    """
    Example subclass of the NetworkX MultiDiGraph class.

    Each edge is assigned a globally unique key.

    self.edges_dict maps edge keys to (u, v, data) tuples.
    This can be useful for algorithms that are primarily edge-based.

    """
    _next_key = 0
    edges_dict = OrderedDict()

    def _keyfunc(self, u, v):
        key = self._next_key
        self._next_key += 1
        return key

    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        # ignore passed in key
        base = super(MultiDiGraph, self)
        key = base.add_edge(u, v, attr_dict=attr_dict, **attr)
        self.edges_dict[key] = (u, v, self.succ[u][v][key])
        return key

    def remove_edge(self, u, v, key=None):
        base = super(MultiDiGraph, self)
        key, data = base.remove_edge(u, v, key=key)
        del self.edges_dict[key]
        return key, data

    def remove_edge_with_key(self, key):
        u, v, _ = self.edges_dict[key]
        k, data = self.remove_edge(u, v, key=key)
        return k, data

    def get_edge_data_with_key(self, key):
        u, v, data = self.edges_dict[key]
        return data

    def size(self):
        return len(self.edges_dict)

def main():
    G = MultiDiGraph()
    k1 = G.add_edge(0, 1, color='red')
    k2 = G.add_edge(0, 1, color='blue')
    G.remove_edge(0, 1, key=k1)
    data = G.remove_edge_with_key(k2)
    G.add_cycle(range(5, 10), weight=3)

    for key, val in G.edges_dict.items():
        print(key)
        print(val)
        print()


if __name__=='__main__':
    main()
