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

    def __setitem__(self,graph_class,(test_str,setup_str)):
        """
        Set a simlpe bit of code and setup string for the test.
        Use this for cases where the code differs from one class to another.
        """
        if graph_class == 'all':
            graph_class = self.class_tests.keys()
        elif not isinstance(graph_class,list):
            graph_class = [graph_class]

        for GC in graph_class:
            setup_string='import networkx as NX\nG=NX.%s.%s()\n'%(GC.lower(),GC) \
                    + setup_str
            self.class_tests[GC] = Timer(test_str, setup_string)

    def run(self):
        """Run the benchmark for each class and print results."""
        column_len = max(len(G) for G in self.class_tests)

        if self.title:
            print self.title
        print 'Doing %d runs, each with %d reps.' % (self.runs,self.reps)
        print '-'*72

        for GC,timer in self.class_tests.items():
            name = GC.ljust(column_len)
            try:
                print "%s: %s" % (name, timer.repeat(self.runs,self.reps))
            except Exception, e:
                print "%s: Failed to benchmark (%s)." % (name,e)

        print '-'*72
        print

if __name__ == "__main__":
    # set up for all routines:
    classes=['Graph','XGraph','DiGraph','XDiGraph']
    all_tests=['add_nodes','add_edges','delete_nodes','delete_edges',\
            'neighbors','edges','degree','dijkstra','shortest path',\
            'subgraph','laplacian']
    # Choose which tests to run
    #tests=all_tests
    tests=all_tests[-1:]
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

    if 'delete_nodes' in tests:
        title='Benchmark: Adding and Deleting nodes'
        setup='nlist=range(%i)'%N
        test_string=('G.add_nodes_from(nlist)\nG.delete_nodes_from(nlist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'delete_edges' in tests:
        title='Benchmark: Adding and Deleting edges'
        setup='elist=[(i,i+3) for i in range(%s-3)]'%N
        test_string=('G.add_edges_from(elist)\n G.delete_edges_from(elist)',setup)
        b=Benchmark(classes,title,test_string,runs=3,reps=1000)
        b.run()

    if 'neighbors' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting neighbors'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='for n in G:\n for nbr in G.neighbors(n):\n  pass'
        all_setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)\n'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'edges' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting edges'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='for n in G:\n for e in G.edges(n):\n  pass'
        all_setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)\n'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'degree' in tests:
        N=500
        p=0.3
        title='Benchmark: reporting degree'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='for d in G.degree():\n  pass'
        all_setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)\n'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'dijkstra' in tests:
        N=500
        p=0.3
        title='dijkstra single source shortest path'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='p=NX.single_source_dijkstra(G,i)'
        all_setup='i=6\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'shortest path' in tests:
        N=500
        p=0.3
        title='single source shortest path'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='p=NX.single_source_shortest_path(G,i)'
        all_setup='i=6\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'subgraph' in tests:
        N=500
        p=0.3
        title='subgraph method'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='G.subgraph(nlist)'
        all_setup='nlist=range(100,150)\nH=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()

    if 'laplacian' in tests:
        N=500
        p=0.3
        title='creation of laplacian matrix'
        b=Benchmark(classes,title,runs=3,reps=1)
        test_string='NX.laplacian(G)'
        all_setup='H=NX.binomial_graph(%s,%s)\nfor (u,v) in H.edges_iter():\n '%(N,p)
        setup=all_setup+'G.add_edge(u,v)'
        b['Graph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v),(v,u)])'
        b['DiGraph']=(test_string,setup)
        setup=all_setup+'G.add_edge(u,v,1)' 
        b['XGraph']=(test_string,setup)
        setup=all_setup+'G.add_edges_from([(u,v,1),(v,u,1)])'
        b['XDiGraph']=(test_string,setup)
        b.run()
