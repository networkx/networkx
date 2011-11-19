
from nose.tools import assert_equal

import networkx as nx

def test_smetric():
    g = nx.Graph()
    g.add_edge(1,2)
    g.add_edge(2,3)
    g.add_edge(2,4)
    g.add_edge(1,4)
    sm = nx.s_metric(g,normalized=False)
    assert_equal(sm, 19.0)
#    smNorm = nx.s_metric(g,normalized=True)
#    assert_equal(smNorm, 0.95)

