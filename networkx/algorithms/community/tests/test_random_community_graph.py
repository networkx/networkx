import networkx as nx
from nose.tools import *

    
def test_LFR_benchmark_graph():
    G = nx.LFR_benchmark_graph(250,
                               3,
                               1.5,
                               0.1,
                               average_degree=5,
                               min_community=20,
                               seed=10)
    C = G.graph['partition']
    #assert_equal([len(c) for c in C], [53,12,10,15,10])
    assert_equal(len(G),250)
    #Aassert_equal(len(G.edges()),157)
    assert_true(nx.is_partition(G.nodes(),C))
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  1.0,
                  2.0,
                  .1,
                  min_degree=2)
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  2.0,
                  1.0,
                  .1,
                  min_degree=2)
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  2.0,
                  2.0,
                  1.1,
                  min_degree=2)
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  2.0,
                  2.0,
                  -1.0,
                  min_degree=2)
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  2.0,
                  2.0,
                  .1,
                  min_degree=None,
                  average_degree=None)
    assert_raises(nx.NetworkXError,
                  nx.LFR_benchmark_graph,
                  100,
                  2.0,
                  1.5,
                  .1,
                  min_degree=2,
                  average_degree=5)
