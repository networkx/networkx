#!/usr/bin/env python
from __future__ import print_function
from nose.tools import *
from collections import OrderedDict
import networkx as nx
from timeit import Timer

# dict pointing to graph type to compare to.
graph_type = {
        (False, False): "TimingGraph",
        (False, True): "TimingMultiGraph",
        (True, False): "TimingDiGraph",
        (True, True): "TimingMultiDiGraph"
        }

# Setup tests
N,p = 200,0.1
basic_setup=('for (u,v) in NX.binomial_graph(%s,%s).edges():\n'
             ' G.add_weighted_edges_from([(u,v,2),(v,u,2)])'%(N,p)
            )
elist_setup=('elist=[(i,i+3) for i in range(%s-3)]\n'
             'G.add_nodes_from(range(%i))'%(N,N)
            )
all_tests=[
    # Format: (name, (test_string, setup_string, runs, reps, cutoff_ratio)),
    ('add_nodes',
        ('G.clear()\nG.add_nodes_from(nlist)', 'nlist=range(%i)'%N, 3, 10)),
    ('add_edges', ('G.add_edges_from(elist)', elist_setup, 3, 10) ),
    ('add_and_remove_nodes',
        ('G.add_nodes_from(nlist)\nG.remove_nodes_from(nlist)',
         'nlist=range(%i)'%N, 3, 10) ),
    ('add_and_remove_edges',
        ('G.add_edges_from(elist)\nG.remove_edges_from(elist)',
         elist_setup, 3, 10) ),
    ('neighbors',
        ('for n in G:\n for nbr in G.neighbors(n):\n  pass',
         basic_setup, 3, 1) ),
    ('edges',
        ('for n in G:\n for e in G.edges(n):\n  pass', basic_setup, 3, 1) ),
    ('edge_data',
        ('for n in G:\n for e in G.edges(n,data=True):\n  pass',
            basic_setup, 3, 1) ),
    ('all_edges',
        (('for n,nbrs in G.adjacency():\n'
          ' for nbr,data in nbrs.items():\n  pass'),
            basic_setup, 3, 1) ),
    ('degree', ('for d in G.degree():\n  pass', basic_setup, 3, 1) ),
    ('copy', ('H=G.copy()', basic_setup, 3, 1) ),
    ('dijkstra',
        ('p=NX.single_source_dijkstra(G,i)', 'i=6\n'+basic_setup, 3, 1) ),
    ('shortest_path',
        ('p=NX.single_source_shortest_path(G,i)',
         'i=6\n'+basic_setup, 3, 1) ),
    ('subgraph',
        ('G.subgraph(nlist)',
         'nlist=range(100,150)\n'+basic_setup, 3, 1) ),
    #('numpy_matrix', ('NX.to_numpy_matrix(G)', basic_setup, 3, 1) ),
  ]


class Benchmark(object):
    """
    Class to benchmark (time) various Graph routines.

    Parameters
    ----------
    graph_classes :  List of classes to test.
    tests : List of tests to run on each class.

    Format for tests:
    (name, (test_string, setup_string, runs, repeats, [cutoff_ratio]))

    name: A string used to identify this test when reporting results.
    test_string: The code-string used repeatedly in the test.
    setup_string: The code-string used once before running the test.
        Some text is prepended to setup_string. It imports NetworkX
        and creates an instance (called G) of the tested graph class.
    runs: Number of timing runs.
    repeats: Number of repeats of the test for each run.
    cutoff_ratio: optional ratio of times [current/TimingClass]
        If (ratio > cutoff_ratio) then check_ratios() returns False.

    Notes
    -----
    Benchmark uses the timeit package and timeit.Timer class.
    """
    def __init__(self, graph_classes, tests=all_tests):
        self.gc = graph_classes
        self.tests = tests

    def run(self, verbose=False, cutoff_default=3):
        errors=''
        headers=list(self.gc)
        if verbose:
            raw_times=" ".join( gc.rjust(12) for gc in headers )
            print('Raw Times'.ljust(23) + raw_times)
            print("="*79, end=" ")
        results=[]  # for each test list times for each graph_class
        for tst,params in self.tests:
            if verbose:
                print()  #add newline
                print(tst.ljust(22), end=" ")
            times=[]
            for gc in headers:
                t,bt = self.time_me(gc, tst, params[:4])
                cutoff=params[4] if len(params)>4 else cutoff_default
                rat=t/bt
                times.append( (tst, params, gc, t, bt, rat, cutoff) )
                if rat > cutoff:
                    errors+='Timing "'+tst+'" failed for class "'+gc+'". '
                    errors+='Time ratio (new/base): {:f}\n'.format(rat)
                if verbose:
                    print("{:12.3e}".format(t), end=" ")
            results.append(times)
        if verbose:
            print('\n')
            hdrs=" ".join(gc.rjust(12) for gc in headers)
            print('Time Ratio to Baseline'.ljust(23) + hdrs)
            print("="*(23+len(hdrs)))
            for res in results:
                tst=res[0][0]
                output = " ".join( "{:12.3f}".format(t[5]) for t in res )
                print(tst.ljust(23) + output)
        self.results=results
        if errors != '':
            print(errors)
            return False #not all passed
        return True #all passed

    def time_me(self, gc, tst, params):
        """ Time the test for class gc and its comparison TimingClass """
        stmt,t_setup,runs,reps = params
        #
        setup="import networkx as NX\nG=NX.%s()\n"%gc + t_setup
        G = eval("nx."+gc+"()")
        cc = graph_type[ (G.is_directed(), G.is_multigraph()) ]
        compare_setup=("import networkx as NX\n"
                       "import timingclasses as tc\n"
                       "G=tc.%s()\n"%(cc,)) + t_setup
        #
        tgc = Timer(stmt, setup)
        tcc = Timer(stmt, compare_setup)
        #
        t = tgc.repeat(repeat = runs, number = reps)
        bt = tcc.repeat(repeat = runs, number = reps)
        return min(t),min(bt)

# The fluctuations in timing make this problematic for travis-CI
# uncomment it to use with nosetests.
#class Test_Benchmark(Benchmark):
#    """ Class to allow nosetests to perform benchmark tests """
#    def __init__(self):
#        classes=['Graph','MultiGraph','DiGraph','MultiDiGraph']
#        self.gc = classes
#        self.tests = all_tests
#
#    def test_ratios(self):
#        assert_true(self.run(verbose=False, cutoff_default=3))

if __name__ == "__main__":
    classes=['Graph','MultiGraph','DiGraph','MultiDiGraph']
#    classes=['SpecialGraph','SpecialMultiGraph',\
#            'SpecialDiGraph','SpecialMultiDiGraph']
    b=Benchmark(classes,tests=all_tests)
#    b=Benchmark(classes,tests=dict( (k,v) for k,v in all_tests.items() if "add" in k ))
    assert b.run(verbose=True)
