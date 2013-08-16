import time
import networkx as nx
from networkx.algorithms.approximation import approx_clustering_coefficient

def test_simple():
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(1, 3)
    acc = approx_clustering_coefficient(G)
    assert acc == 1.0, "Approximated clustering coefficient is wrong, should be 1.0, was %f" % (acc,)
    return acc

def test_complete(n=10000):
    #create a watts strogatz graph 
    G = nx.complete_graph(n)
    acc = approx_clustering_coefficient(G)
    assert acc == 1.0, "Approximated clustering coefficient is wrong, should be 1.0, was %f" % (acc,)
    return acc

def test_graph(G=None, num_trials=1000):
    #make the wheel if we have no graph
    if G == None:
      G = nx.wheel_graph(5000)

    #run the real computation for comparison
    st = time.time()
    true_cc = nx.average_clustering(G)
    full_time = time.time() - st
    print "\tFull computation took %f seconds" % (full_time,)

    #run the estimation
    st = time.time()
    acc = approx_clustering_coefficient(G, num_trials)
    est_time = time.time() - st
    print "\tApproximation took %f seconds" % (est_time,)

    #calculate some properties of the two computations
    time_gain = full_time / est_time
    error_percentage = abs(acc - true_cc) * 100

    print "\tApproximation was %1.2fx faster with %1.2f%% error." % (time_gain, error_percentage)

    #we can accept 5% error
    acceptable_error = 5
    assert error_percentage <= acceptable_error, "Unacceptably wrong clustering coefficient. Real CC: %f, Estimated: %f" % (true_cc, acc)
    print "\tClustering Coefficient (actual, approximated): (%f, %f)" % (true_cc, acc)
    return acc, error_percentage

def main():
    # First, try a complete graph (just for timing's sake).
    print "=== Complete Graph (n = 10e3, k = 10e4) ==="
    G = nx.complete_graph(1000)
    test_graph(G, num_trials=10000)

    print "=== 5 trials: Watts-Strogatz (n = 10e3, k = 150, p = 0.4) ==="
    G = nx.watts_strogatz_graph(1000, 150, 0.4)
    num_trials = 5
    total_error = 0.
    for i in xrange(num_trials):
      (acc, er) = test_graph(G)
      total_error += er
    print "=== Average Error: %2.2f%% ===" % (total_error / num_trials,)

if __name__ =='__main__':main()

