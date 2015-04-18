from nose.tools import *
import networkx as nx
import sys
sys.path.append('..')
from exact_maximum_independent_set import*

def test_independent_set():
    # smoke test
    G = nx.Graph()
    assert_equal(len(maximum_independent_set(G)),0)
    #complete graph
    G = nx.complete_graph(30)
    mi = maximum_independent_set(G)
    assert_equals(1, len(mi))
