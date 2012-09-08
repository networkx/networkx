import networkx as nx
from nose.tools import *
def test_modularity():
    G = nx.barbell_graph(3,0)
    C = [set([0,1,4]),set([2,3,5])]
    assert_almost_equal(-16/(14.**2),nx.modularity(G,C))
    C = [set([0,1,2]),set([3,4,5])]
    assert_almost_equal((35*2)/(14**2.),nx.modularity(G,C))

