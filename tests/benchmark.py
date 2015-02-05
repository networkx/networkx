from timeit import Timer

# This is gratefully modeled after the benchmarks found in
# the numpy svn repository.  http://svn.scipy.org/svn/numpy/trunk

class Benchmark(object):
    """
    Benchmark a method or simple bit of code using different Graph classes.
    If the test code is the same for each graph class, then you can set it
    during instantiation through the argument test_string.
    The argument test_string can also be a tuple of test code and setup code.
    The code is entered as a string valid for use with the timeit module.

    Example:
    >>> b=Benchmark(['Graph','XGraph'])
    >>> b['Graph']=('G.add_nodes_from(nlist)','nlist=range(100)')
    >>> b.run()
    """
    def __init__(self,graph_classes,title='',test_string=None,runs=3,reps=1000):
        self.runs = runs
        self.reps = reps
        self.title = title
        self.class_tests = dict((gc,'') for gc in graph_classes)
        # set up the test string if it is the same for all classes.
        if test_string is not None:
            if isinstance(test_string,tuple):
                self['all']=test_string
            else:
                self['all']=(test_string,'')

    def __setitem__(self,graph_class,some_strs):
        """
        Set a simple bit of code and setup string for the test.
        Use this for cases where the code differs from one class to another.
        """
        test_str, setup_str = some_strs
        if graph_class == 'all':
            graph_class = self.class_tests.keys()
        elif not isinstance(graph_class,list):
            graph_class = [graph_class]

        for GC in graph_class:
#            setup_string='import networkx as NX\nG=NX.%s.%s()\n'%(GC.lower(),GC) \
#                    + setup_str
            setup_string='import networkx as NX\nG=NX.%s()\n'%(GC,) \
                    + setup_str
            self.class_tests[GC] = Timer(test_str, setup_string)


    def run(self):
        """Run the benchmark for each class and print results."""
        column_len = max(len(G) for G in self.class_tests)

        print('='*72)
        if self.title:
            print("%s: %s runs, %s reps"% (self.title,self.runs,self.reps))
        print('='*72)

        times=[]
        for GC,timer in self.class_tests.items():
            name = GC.ljust(column_len)
            try:
#                t=sum(timer.repeat(self.runs,self.reps))/self.runs
                t=min(timer.repeat(self.runs,self.reps))
#                print "%s: %s" % (name, timer.repeat(self.runs,self.reps))
                times.append((t,name))
            except Exception as e:
                print("%s: Failed to benchmark (%s)." % (name,e))


        times.sort()
        tmin=times[0][0]
        for t,name in times:
            print("%s: %5.2f %s" % (name, t/tmin*100.,t))
        print('-'*72)
        print()

if __name__ == "__main__":
    # set up for all routines:
    classes=['Graph','MultiGraph','DiGraph','MultiDiGraph']
#    classes=['Graph','MultiGraph','DiGraph','MultiDiGraph',
#            'SpecialGraph','SpecialDiGraph','SpecialMultiGraph','SpecialMultiDiGraph']
#    classes=['Graph','SpecialGraph']
    all_tests=['add_nodes','add_edges','remove_nodes','remove_edges',\
            'neighbors','edges','degree','dijkstra','shortest path',\
            'subgraph','edgedata_subgraph','laplacian']
    # Choose which tests to run
    tests=all_tests
#    tests=['edges','laplacian']
    #tests=all_tests[-1:]
    N=100

    if 'add_nodes' in tests:
        title='Benchmark: Adding nodes'
        test_string=('G.add_nodes_from(nlist)','nlist=range(%i)'%N)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'add_edges' in tests:
        title='Benchmark: Adding edges'
        setup='elist=[(i,i+3) for i in range(%s-3)]\nG.add_nodes_from(range(%i))'%(N,N)
        test_string=('G.add_edges_from(elist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'remove_nodes' in tests:
        title='Benchmark: Adding and Deleting nodes'
        setup='nlist=range(%i)'%N
        test_string=('G.add_nodes_from(nlist)\nG.remove_nodes_from(nlist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'remove_edges' in tests:
        title='Benchmark: Adding and Deleting edges'
        setup='elist=[(i,i+3) for i in range(%s-3)]'%N
        test_string=('G.add_edges_from(elist)\nG.remove_edges_from(elist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'neighbors' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting neighbors'
        setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('for n in G:\n for nbr in G.neighbors(n):\n  pass',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'edges' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting edges'
        setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('for n in G:\n for e in G.edges(n):\n  pass',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'degree' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting degree'
        setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('for d in G.degree():\n  pass',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'dijkstra' in tests:
        N=500
        p=0.3
        title='dijkstra single source shortest path'
        setup='i=6\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('p=NX.single_source_dijkstra(G,i)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'shortest path' in tests:
        N=500
        p=0.3
        title='single source shortest path'
        setup='i=6\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('p=NX.single_source_shortest_path(G,i)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'subgraph' in tests:
        N=500
        p=0.3
        title='subgraph method'
        setup='nlist=range(100,150)\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('G.subgraph(nlist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'edgedata_subgraph' in tests:
        N=500
        p=0.3
        title='subgraph method with edge data present'
        setup='nlist=range(100,150)\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v,dict(hi=2)),(v,u,dict(hi=2))])'%(N,p)
        test_string=('G.subgraph(nlist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=10)
        b.run()

    if 'laplacian' in tests:
        N=500
        p=0.3
        title='creation of laplacian matrix'
        setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n G.add_edges_from([(u,v),(v,u)])'%(N,p)
        test_string=('NX.laplacian_matrix(G)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1)
        b.run()
