"""
Base class for XDiGraph.

XDiGraph allows directed graphs with self-loops, multiple edges, 
arbitrary (hashable) objects as nodes, and arbitrary objects
associated with edges.


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.digraph import DiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class XDiGraph(DiGraph):
    """
    Digraphs with (optional) self-loops, (optional) multiple edges,
    arbitrary (hashable) objects as nodes, and arbitrary
    objects associated with edges.

    An XDiGraph edge is uniquely specified by a 3-tuple
    e=(n1,n2,x), where n1 and n2 are (hashable) objects (nodes) and x
    is an arbitrary (and not necessarily unique) object associated with
    that edge.

    See the documentation of XGraph for the use of the optional
    parameters selfloops (defaults is False) and multiedges
    (default is False).

    XDiGraph inherits from DiGraph, with all purely node-specific methods
    identical to those of DiGraph. XDiGraph edges are identical to XGraph
    edges, except that they are directed rather than undirected.
    XDiGraph replaces the following DiGraph methods:

    - __init__: read multiedges and selfloops optional args.
    - add_edge
    - add_edges_from
    - delete_edge
    - delete_edges_from
    - has_edge
    - has_predecessor
    - has_successor
    - get_edge
    - edges_iter
    - in_edges_iter
    - out_edges_iter
    - neighbors_iter
    - successors_iter
    - predecessors_iter
    - degree_iter
    - out_degree_iter
    - in_degree_iter
    - subgraph
    - copy
    - to_undirected
    - reverse
    
    XDiGraph also adds the following methods to those of DiGraph:

    - allow_selfloops
    - remove_all_selfloops
    - ban_selfloops
    - nodes_with_selfloops
    - self_loop_edges
    - number_of_selfloops

    - delete_multiedge
    - allow_multiedges
    - ban_multiedges
    - remove_all_multiedges

    While XDiGraph does not inherit from XGraph, we compare them here.
    XDigraph adds the following methods to those of XGraph:

    - has_successor
    - successors
    - successors_iter
    - has_predecessor
    - predecessors
    - predecessors_iter
    - out_degree
    - out_degree_iter
    - in_degree
    - in_degree_iter
    - reverse

    """
#    XDiGraph, like DiGraph, uses two adjacency lists:
#    predecessors of node n are stored in the dict
#    self.pred successors of node n are stored in the
#    dict self.succ=self.adj
#
#    For each edge (n1,n2,x) in self.succ there exists a corresponding edge
#    (n2,n1,x) in self.pred

    def __init__(self, data=None, name='', selfloops=False, multiedges=False):
        """Initialize XDiGraph.

        Optional arguments::
        name: digraph name (default="No Name")
        selfloops: if True then selfloops are allowed (default=False)
        multiedges: if True then multiple edges are allowed (default=False)

        """
        self.adj={}         # adjacency list
        self.pred={}        # predecessor
        self.succ=self.adj  # successor is same as adj
        self.selfloops=selfloops
        self.multiedges=multiedges
        if data is not None:
            convert.from_whatever(data,create_using=self)
        self.name=name


    def add_edge(self, n1, n2=None, x=None):  
        """Add a single directed edge to the digraph.

        Can be called as G.add_edge(n1,n2,x)
        or as G.add_edge(e), where e=(n1,n2,x).

        If called as G.add_edge(n1,n2) or G.add_edge(e), with e=(n1,n2),
        then this is interpreted as adding the edge (n1,n2,None) to
        be compatible with the Graph and DiGraph classes.

        n1,n2 are node objects, and are added to the Graph if not already
        present.  Nodes must be hashable Python objects (except None).

        x is an arbitrary (not necessarily hashable) object associated
        with this edge. It can be used to associate one or more,
        labels, data records, weights or any arbirary objects to
        edges. The default is the Python None.

        For example, if the graph G was created with

        >>> G=XDiGraph()

        then G.add_edge(1,2,"blue") will add the directed edge (1,2,"blue").

        If G.multiedges=False, then a subsequent G.add_edge(1,2,"red")
        will change the above edge (1,2,"blue") into the edge (1,2,"red").
        
        On the other hand, if G.multiedges=True, then two successive calls to
        G.add_edge(1,2,"red") will result in 2 edges of the form
        (1,2,"red") that can not be distinguished from one another.
        
        If self.selfloops=False, then any attempt to create a self-loop
        with add_edge(n1,n1,x) will have no effect on the digraph and
        will not elicit a warning.

        Objects imbedded in the edges from n1 to n2 (if any), can be
        retrieved using get_edge(n1,n2), or calling edges(n1) or
        edge_iter(n1) to return all edges attached to n1.

        """

        if n2 is None: # add_edge was called as add_edge(e), with e a tuple
            if len(n1)==3: #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1   # x=None


        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(n1,n2,x):
            return

        # add nodes            
        if n1 not in self.succ:
            self.succ[n1]={}
        if n1 not in self.pred:
            self.pred[n1]={}
        if n2 not in self.succ:
            self.succ[n2]={}
        if n2 not in self.pred:
            self.pred[n2]={}

        # self loop? quietly return if not allowed
        if not self.selfloops and n1==n2: 
            return

        if self.multiedges: # append x to the end of the list of objects
                            # that defines the edges between n1 and n2
            self.succ[n1][n2]=self.succ[n1].get(n2,[])+ [x]
            self.pred[n2][n1]=self.pred[n2].get(n1,[])+ [x]
        else:  # x is the new object assigned to single edge between n1 and n2
            self.succ[n1][n2]=x
            self.pred[n2][n1]=x # note that the same object is referred to
                                # from both succ and pred

    def add_edges_from(self, ebunch):  
         """Add multiple directed edges to the digraph.
         ebunch: Container of edges. Each edge e in container will be added
         using add_edge(e). See add_edge documentation.
         The container must be iterable or an iterator.
         It is iterated over once.
         """
         for e in ebunch:
             # the function-call-in-a-loop cost can be avoided by pasting
             # in the code from add_edge, do we have a good reason ?
             self.add_edge(e)
        
    def has_edge(self, n1, n2=None, x=None):
        """Return True if digraph contains directed edge (n1,n2,x).

        Can be called as G.has_edge(n1,n2,x)
        or as G.has_edge(e), where e=(n1,n2,x).

        If x is unspecified, i.e. if called with an edge of the form
        e=(n1,n2), then return True if there exists ANY edge from n1
        to n2 (equivalent to has_successor(n1,n2)).

        """
        # parse args
        if n2 is None:
            # has_edge was called as has_edge(e)
            if len(n1)==3: # case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # case=(n1,n2)
                n1,n2=n1   # return True if there exists ANY edge n1->n2
                return self.has_successor(n1,n2)
        else:
            if x is None:
                # has_edge was called as has_edge(n1,n2)
                # return True if there exists ANY edge n1->n2
                return self.has_successor(n1,n2)
        # case where x is specified
        if self.multiedges:
            return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2) and
                x in self.succ[n1][n2])
        else:
            return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2) and
                x==self.succ[n1][n2])            

    def has_successor(self, n1, n2):
        """Return True if node n1 has a successor n2.

        Return True if there exists ANY edge (n1,n2,x) for some x.

         """
        return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2))

    def has_predecessor(self, n1, n2):
        """Return True if node n1 has a predecessor n2.

        Return True if there exists ANY edge (n2,n1,x) for some x.

        """
        return (self.pred.has_key(n1) and
                self.pred[n1].has_key(n2))    
    
    def delete_multiedge(self, n1, n2):
        """ Delete all edges between nodes n1 and n2.

        When there is only a single edge allowed between nodes
        (multiedges=False), this just calls delete_edge(n1,n2),
        otherwise (multiedges=True) all edges between n1 and n2 are deleted.
        """
        if self.multiedges:
            for x in self.get_edge(n1,n2):
                self.delete_edge(n1,n2,x)
        else:
            self.delete_edge(n1,n2)
        return


    def delete_edge(self, n1, n2=None, x=None, all=False): 
        """Delete the directed edge (n1,n2,x) from the graph.

        Can be called either as
        >>> G.delete_edge(n1,n2,x)
        or as
        >>> G.delete_edge(e)
        where e=(n1,n2,x).

        If called with an edge e=(n1,n2), or as G.delete_edge(n1,n2)
        then the edge (n1,n2,None) will be deleted.

        If the edge does not exist, do nothing.

        To delete *all* edges between n1 and n2 use
        >>> G.delete_multiedges(n1,n2)

        """
        if n2 is None: #  was called as delete_edge(e)
            if len(n1)==3:  #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1   # x=None

        if self.multiedges:              # multiedges are stored as a list
           if (self.succ.has_key(n1)
               and self.succ[n1].has_key(n2)
               and x in self.succ[n1][n2]):
                self.succ[n1][n2].remove(x)  # remove the edge item from list
                self.pred[n2][n1].remove(x)
                if len(self.succ[n1][n2])==0: # if last edge between n1 and n2
                    del self.succ[n1][n2]     # was deleted, remove all trace
                    del self.pred[n2][n1]
        else:  # delete single edge
            if self.has_successor(n1,n2):
                del self.succ[n1][n2]
                del self.pred[n2][n1]
        return

    def delete_edges_from(self, ebunch): 
        """Delete edges in ebunch from the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2).  The container must be
        iterable or an iterator, and is iterated over once.

        Edges that are not in the graph are ignored.

        """
        for e in ebunch:
            self.delete_edge(e)

    def out_edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge pointing
        out of nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if self.multiedges:
            for n1 in bunch:
                for n2,elist in self.succ[n1].iteritems():
                    for data in elist:
                        yield (n1,n2,data)
        else:
            for n1 in bunch:
                for n2,data in self.succ[n1].iteritems():
                    yield (n1,n2,data)

    def in_edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge pointing in
        to nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if self.multiedges:
            for n1 in bunch:
                for n2,elist in self.pred[n1].iteritems():
                    for data in elist:
                        yield (n2,n1,data)
        else:
            for n1 in bunch:
                for n2,data in self.pred[n1].iteritems():
                    yield (n2,n1,data)

    def successors_iter(self, n):
        """Return an iterator of nodes pointing out of node n. 

        Returns the same data as out_edges(n) but in a different format.

        """
        if n not in self:
            raise NetworkXError, "node %s not in graph"%n
        for (u,v,d) in self.out_edges_iter(n):
            yield v

    def predecessors_iter(self, n):
        """Return an iterator of nodes pointing in to node n. 

        Returns the same data as in_edges(n) but in a different format.

        """
        if n not in self:
            raise NetworkXError, "node %s not in graph"%n
        for (u,v,d) in self.in_edges_iter(n):
            yield u

    edges_iter=out_edges_iter
    neighbors_iter=successors_iter

    def in_degree_iter(self, nbunch=None, with_labels=False):
        """Return iterator for in_degree(n) or (n,in_degree(n))
        for all n in nbunch.
        
        If nbunch is ommitted, then iterate over *all* nodes.
        
        See degree_iter method for more details.
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if self.multiedges:
            if with_labels:   # yield tuple (n,in_degree)
                for n in bunch:
                    yield (n,sum([len(edge) for edge in self.pred[n].itervalues()]))
            else:
                for n in bunch:
                    yield sum([len(edge) for edge in self.pred[n].itervalues()])
        else: 
            if with_labels:   # yield tuple (n,in_degree)
                for n in bunch:
                    yield (n,len(self.pred[n]))
            else:
                for n in bunch:
                    yield len(self.pred[n])

    def out_degree_iter(self, nbunch=None, with_labels=False):
        """Return iterator for out_degree(n) or (n,out_degree(n))
        for all n in nbunch.
        
        If nbunch is ommitted, then iterate over *all* nodes.
        
        See degree_iter method for more details.
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if self.multiedges:
            if with_labels:
                for n in bunch:
                    yield (n,sum([len(edge) for edge in self.succ[n].itervalues()]))
            else:
                for n in bunch:
                    yield sum([len(edge) for edge in self.succ[n].itervalues()])
        else:
            if with_labels:
                for n in bunch:
                    yield (n,len(self.succ[n]))
            else:
                for n in bunch:
                    yield len(self.succ[n])

    def degree_iter(self, nbunch=None, with_labels=False):
        """Return iterator that returns in_degree(n)+out_degree(n)
        or (n,in_degree(n)+out_degree(n)) for all n in nbunch. 
        If nbunch is ommitted, then iterate over *all* nodes.
 
        Can be called in three ways:
        G.degree_iter(n):       return iterator the degree of node n
        G.degree_iter(nbunch):  return a list of values,
        one for each n in nbunch (nbunch is any iterable container of nodes.)
        G.degree_iter():        same as nbunch = all nodes in graph.
 
        If with_labels=True, iterator will return an
        (n,in_degree(n)+out_degree(n)) tuple of node and degree.
 
        Any nodes in nbunch but not in the graph will be (quietly) ignored.
 
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if self.multiedges:
            for n in bunch:
                d=sum([len(e) for e in self.succ[n].itervalues()]) + \
                  sum([len(e) for e in self.pred[n].itervalues()])
                if with_labels:
                    yield (n,d)
                else:
                    yield d
        else:
            for n in bunch:
                d=len(self.succ[n])+len(self.pred[n])
                if with_labels:
                    yield (n,d)
                else:
                    yield d

    def nodes_with_selfloops(self):
        """Return list of all nodes having self-loops."""
        if not self.selfloops:
            return []
        else:
            # only need to do this for succ
            return [n for n in self if self.succ[n].has_key(n)]

    def selfloop_edges(self):
        """Return all edges that are self-loops."""
        nlist=self.nodes_with_selfloops()
        if self.multiedges:
            return [ (n,n,x) for n in nlist for x in self.adj[n][n]]
        else:
            return [ (n,n,self.adj[n][n]) for n in nlist ]
            
    def number_of_selfloops(self):
        """Return number of self-loops in graph."""
        nlist=self.nodes_with_selfloops()
        if self.multiedges:
            return sum([ len(self.adj[n][n]) for n in nlist])
        else:
            return len(nlist)

    def allow_selfloops(self):
        """Henceforth allow addition of self-loops
        (edges from a node to itself).

        This doesn't change the graph structure, only what you can do to it.
        """
        self.selfloops=True

    def remove_all_selfloops(self):
        """Remove self-loops from the graph (edges from a node to itself)."""
        for n in self.succ:
            if self.succ[n].has_key(n):
                del self.succ[n][n]
                del self.pred[n][n]
 
    def ban_selfloops(self):
        """Remove self-loops from the graph and henceforth do not allow
        their creation.
        """
        self.remove_all_selfloops()
        self.selfloops=False


    def allow_multiedges(self):
        """Henceforth allow addition of multiedges (more than one
        edge between two nodes).  

        Warning: This causes all edge data to be converted to lists.
        """
        if self.multiedges: return # already multiedges
        self.multiedges=True
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                self.succ[v][u]=[edgedata]
                self.pred[u][v]=[edgedata]

    def remove_all_multiedges(self):
        # FIXME, write tests
        """Remove multiedges retaining the data from the first edge"""
        if not self.multiedges: # nothing to do
            return
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                if len(edgedata)>1:
                    self.succ[v][u]=[edgedata[0]]
                    self.pred[u][v]=[edgedata[0]]

    def ban_multiedges(self):
        """Remove multiedges retaining the data from the first edge.
        Henceforth do not allow multiedges.
        """
        if not self.multiedges: # nothing to do
            return
        self.multiedges=False
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                self.succ[v][u]=edgedata[0]
                self.pred[u][v]=edgedata[0]
        
    def subgraph(self, nbunch, inplace=False, create_using=None):
        """Return the subgraph induced on nodes in nbunch.

        nbunch: can be a singleton node, a string (which is treated
        as a singleton node), or any iterable container of
        of nodes. (It can be an iterable or an iterator, e.g. a list,
        set, graph, file, numeric array, etc.)

       Setting inplace=True will return induced subgraph in original
       graph by deleting nodes not in nbunch. It overrides any setting
       of create_using.

       WARNING: specifying inplace=True makes it easy to destroy the graph.

       Unless otherwise specified, return a new graph of the same
       type as self.  Use (optional) create_using=R to return the
       resulting subgraph in R. R can be an existing graph-like
       object (to be emptied) or R can be a call to a graph object,
       e.g. create_using=DiGraph(). See documentation for
       empty_graph()

       Note: use subgraph(G) rather than G.subgraph() to access the more
       general subgraph() function from the operators module.

        """
        bunch=self.prepare_nbunch(nbunch)

        # WARNING: setting inplace=True destroys the graph.
        if inplace: # demolish all nodes (and attached edges) not in nbunch
                    # override any setting of create_using
            bunch=dict.fromkeys(bunch) # make a dict
            self.delete_nodes_from([n for n in self if n not in bunch])
            self.name="Subgraph of (%s)"%(self.name)
            return self

        # create new graph        
        if create_using is None:
            # return a Graph object of the same type as current graph
            # subgraph inherits multiedges and selfloops settings
            H=self.__class__(multiedges=self.multiedges,
                             selfloops=self.selfloops)
        else:
            # Recreate subgraph with create_using.
            # Currently create_using must be an XGraph type object
            # or a multi-edge list will be copied as a single edge
            H=create_using
            H.clear()
        H.name="Subgraph of (%s)"%(self.name)
        H.add_nodes_from(bunch)
        
        # add edges
        H_succ=H.succ       # store in local variables
        H_pred=H.pred       
        self_succ=self.succ 
        self_pred=self.pred 
        if self.multiedges:
            for n in H:   # create dicts with copies of edge data list from self
                H_succ[n]=dict([(u,d[:]) for u,d in self_succ[n].iteritems() if u in H_succ])
                H_pred[n]=dict([(u,d[:]) for u,d in self_pred[n].iteritems() if u in H_pred])
        else: # no multiedges
            for n in H:   # create dicts with edge data from self
                H_succ[n]=dict([(u,d) for u,d in self_succ[n].iteritems() if u in H_succ])
                H_pred[n]=dict([(u,d) for u,d in self_pred[n].iteritems() if u in H_pred])
        return H

    def copy(self):
        """Return a (shallow) copy of the digraph.

        Return a new XDiGraph with same name and same attributes for
        selfloop and multiededges. Each node and each edge in original
        graph are added to the copy.
        
        """
        H=self.__class__(name=self.name, multiedges=self.multiedges, selfloops=self.selfloops)
        H.add_nodes_from(self)
        H.add_edges_from(self.edges_iter())
        return H        

    def to_undirected(self):
        """Return the underlying graph of G.
        
        The underlying graph is its undirected representation: each directed
        edge is replaced with an undirected edge.

        If multiedges=True, then an XDiGraph with only two directed
        edges (1,2,"red") and (2,1,"blue") will be converted into an
        XGraph with two undirected edges (1,2,"red") and (1,2,"blue").
        Two directed edges (1,2,"red") and (2,1,"red") will result in
        in two undirected edges (1,2,"red") and (1,2,"red").

        If multiedges=False, then two directed edges (1,2,"red") and
        (2,1,"blue") can only result in one undirected edge, and there
        is no guarantee which one it is.
        
        """
        from networkx.xgraph import XGraph
        H=XGraph(name=self.name, multiedges=self.multiedges, selfloops=self.selfloops)
        H.add_nodes_from(self)
        H.add_edges_from(self.edges_iter())
        return H

    def reverse(self):
        """
        Return a new digraph with the same vertices and edges
        as self but with the directions of the edges reversed.
        """
        H=self.__class__(name="Reverse of (%s)"%self.name,\
                multiedges=self.multiedges, selfloops=self.selfloops)
        H.add_nodes_from(self)
        H.add_edges_from( [ (v,u,d) for (u,v,d) in self.edges_iter() ] )
        return H

        
def _test_suite():
    import doctest
    suite = doctest.DocFileSuite(
                                'tests/xdigraph_XDiGraph.txt',
                                 package='networkx')
    return suite


if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
