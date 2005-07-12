""" Graph search classes

The search algorithms are implemented as an abstract class with
visitor functions that are called at points during the algorithm.
By designing different visitor functions the search algorithms
can produce shortest path lenghts, forests of search trees, etc.

The simplest way to access the search algorithms is by using
predefined visitor classes and search functions.
See the module NX.search.

These algorithms are based on Program 18.10 "Generalized graph search",
page 128, Algorithms in C, Part 5, Graph Algorithms by Robert Sedgewick

Reference::

  @Book{sedgewick-2001-algorithms-5,
  author = 	 {Robert Sedgewick},
  title = 	 {Algorithms in C, Part 5: Graph Algorithms},
  publisher = 	 {Addison Wesley Professional},
  year = 	 {2001},
  edition = 	 {3rd},
  }

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-06-15 08:17:35 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1025 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import NX
#from NX import DiGraph
#from queues import DFS,BFS,RFS

class Search(object):
    """
    Generic graph traversal (search) class.
    
    Users should generally use the search functions defined below.
    e.g. to get a list of all nodes of G in breadth first search (BFS)
    order from v use

    vertex_list=bfs_preorder(G,v)
    
    To search the graph G from v do the following:

    S=Search(G,queue=DFS)
    S.search(v=v)

    Depending on the type of queue you will get a different traversal type. 

    You may use any of the following queues from the Queues class:
    Name      Queue    Traversal
    -----     ------   ----------
    DFS       LIFO     Depth First Search 
    BFS       FIFO     Breadth First Search 
    Random    Random   Random search
    
    The generic search produces no data and thus is of limited utility.
    Visitor callback functions are called at points along the search 
    which may be used to store shortest path data 

    """
    def __init__(self, G, queue=NX.queues.DFS):
        self.seen={}        # keep track of nodes seen
        self.tree={}        # keep track of nodes put on search tree 
        self.fringe=queue() # instantiate queue for edges, "the fringe"
        self.G=G

    def search(self, v=None):
        """
        Search the graph.

        The search method is deteremined by the initialization of the
        search object.
        
        The optional v= argument can be a single vertex a list or None.

        v=v:     search the component of G reachable from v
        v=vlist: search the component of G reachable from v
        v=None:  search the entire graph G even if it isn't connected
                   
        Call visitor functions along the way.

        """
        # get starting vertex
        nodes=[]
        if v is None:                # none, use entire graph 
            nodes=self.G.nodes() 
        elif isinstance(v, list):  # check for a list
            nodes=v
        else:                      # assume it is a single value
            nodes=[v]

        # general search that finds all trees
        for v in nodes:      
            if not self.seen.has_key(v): 
                self.start_tree(v)
                e=(v,v)          # form self loop as starting edge 
                self.__search_connected(e) # search the component containing v
                self.end_tree(v)

    def __search_connected(self, e):
        """
        Private method to this class.

        Search a single connected component starting at the edge e.
        To start from a vertex v, use e=(v,v).
        Call the visitor functions along the way.

        """
        (v,w)=e
        self.seen.setdefault(w)     # add to seen nodes dict
        self.firstseen_vertex(w)
        self.fringe.append(e)
        self.firstseen_edge(e)
        while(len(self.fringe)>0):
            e=self.fringe.pop()         # get edge from the fringe
            (v,w)=e
            self.lastseen_edge(e)  
            self.lastseen_vertex(w)
            self.tree.setdefault(w,v)         # and put it on our tree  
            for n in self.G.neighbors(w):     # scan adjacency list at w
                if not self.seen.has_key(n): 
                    self.seen.setdefault(n)    
                    self.firstseen_vertex(n)
                    self.fringe.append((w,n))  # put unseen edges on fringe
                    self.firstseen_edge((w,n))
                elif not self.tree.has_key(n):
                    self.fringe.update((w,n))  
                    self.firstseen_edge((w,n))

    # default visitor functions                    
    def start_tree(self,v):
        """Visitor function called at the search start
           of each connected component.
        """
        pass

    def firstseen_vertex(self,v):
        """Visitor function called the first time a vertex is encountered."""
        pass

    def lastseen_vertex(self,v):
        """Visitor function called the last time a vertex is encountered."""
        pass

    def end_tree(self,v):
        """Visitor function called at the search end
           of each connected component.
        """
        pass

    def firstseen_edge(self,e):
        """Visitor function called the first time an edge is encountered."""
        pass

    def lastseen_edge(self,e):
        """Visitor function called the last time an edge is encountered."""
        pass


class Preorder(Search):
    """ Preorder visitor     
        Builds a list of nodes in preorder of search.
        Returns a list of lists if the graph is not connected.
        """
    def __init__(self, G, queue=NX.queues.DFS, **kwds):
        self.forest=[]
        super(Preorder,self).__init__(G, queue=queue)        

    def start_tree(self,v):
        """Visitor function called at the search start
           of each connected component.
        """
        self.vlist=[]

    def firstseen_vertex(self,v):
        """Visitor function called the first time a vertex is encountered."""
        self.vlist.append(v)

    def end_tree(self,v):
        """Visitor function called at the search end
           of each connected component.
        """
        self.forest.append(self.vlist)


class Postorder(Search):
    """ Postorder visitor     
        Builds a list of nodes in postorder of search.
        Returns a list of lists if the graph is not connected.
        """
    def __init__(self, G, queue=NX.queues.DFS, **kwds):
        self.forest=[]
        super(Postorder,self).__init__(G, queue=queue)        


    def start_tree(self,v):
        """Visitor function called at the search start
           of each connected component.
        """
        self.vlist=[]

    def lastseen_vertex(self,v):
        """Visitor function called the last time a vertex is encountered."""
        self.vlist.append(v)

    def end_tree(self,v):
        """Visitor function called at the search end
           of each connected component.
        """
        self.forest.append(self.vlist)


class Predecessor(Search):
    """ Predeceessor visitor     
        Builds a dict of nodes with sucessor vertex list as data.
        path method returns path lengths from source to target.
        """
    def __init__(self, G, queue=NX.queues.DFS, **kwds):
        self.data={}
        super(Predecessor,self).__init__(G, queue=queue)        


    def firstseen_vertex(self,v):
        """Visitor function called the first time a vertex is encountered."""
        self.data[v]=[]

    def lastseen_edge(self,e):
        """Visitor function called the last time an edge is encountered."""
        (u,v)=e
        if not u==v:
            self.data[v].append(u)


    def path(self, target):
        """Gets one shortest path to target out of predecessor hash.
           There might be more than one 
        """
        path=[]
        if self.data.has_key(target):
            while not self.data[target]==[]: 
                path.append(target)
                target=self.data[target][0]
            path.reverse()                
            return path
        else:
            return []


class Successor(Search):
    """ Successor visitor     
        Builds a dict of nodes with sucessor vertex list as data.
        """
    def __init__(self, G, queue=NX.queues.DFS, **kwds):
        self.data={}
        super(Successor,self).__init__(G, queue=queue)        

    def firstseen_vertex(self,v):
        """Visitor function called the first time a vertex is encountered."""
        self.data.setdefault(v,[])

    def lastseen_edge(self,e):
        """Visitor function called the last time an edge is encountered."""
        (u,v)=e
        if not u==v:
            self.data[u].append(v)

class Length(Search):
    """ Path length visitor.
        Returns dictionary of path lengths from vertex v. 
        Useful especially in BFS (gives shortest paths).
    """
    def __init__(self, G, queue=NX.queues.BFS, **kwds):
        self.length={}
        super(Length,self).__init__(G, queue=queue)        

    def lastseen_edge(self,e):
        """Visitor function called the first time an edge is encountered."""
        (u,v)=e
        if u==v:
            self.length[u]=0         # at start
        else:
            level=self.length[u]     # target is one level higher than source
            self.length[v]=level+1


class Forest(Search):
    """
    Forest visitor: build a forest of trees as a list of NX DiGraphs.
    """
    def __init__(self, G, queue=NX.queues.DFS, **kwds):
        self.forest=[]
        super(Forest,self).__init__(G, queue=queue)        

    def start_tree(self,v):
        """Visitor function called at the search start
           of each connected component.
        """
        self.T=NX.DiGraph()
        self.T.add_node(v)

    def lastseen_edge(self,e):
        """Visitor function called the last time an edge is encountered."""
        (u,v)=e
        if not u==v:
            self.T.add_edge(u,v)

    def end_tree(self,v):
        """Visitor function called at the search end
           of each connected component.
        """
        self.forest.append(self.T)

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/search_class.txt',package='NX')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    

