"""
Base class for XGraph.

XGraph allows self-loops and multiple edges 
with arbitrary (hashable) objects as
nodes and arbitrary objects associated with edges.
    
Examples
========

Create an empty graph structure (a "null graph") with no nodes and no edges

>>> from networkx import *
>>> G=XGraph()  # default no self-loops, no multiple edges

You can add nodes in the same way as the simple Graph class
>>> G.add_nodes_from(xrange(100,110))

You can add edges as for simple Graph class, but with optional edge
data/labels/objects.

>>> G.add_edges_from([(1,2,0.776),(1,3,0.535)])

For graph coloring problems, one could use
>>> G.add_edges_from([(1,2,"blue"),(1,3,"red")])

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#


from networkx.graph import Graph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class XGraph(Graph):
    """A class implementing general undirected graphs, allowing
    (optional) self-loops, multiple edges, arbitrary (hashable)
    objects as nodes and arbitrary objects associated with
    edges.

    An XGraph edge is specified by a 3-tuple e=(n1,n2,x),
    where n1 and n2 are nodes (hashable objects) and x is an
    arbitrary (and not necessarily unique) object associated with that
    edge.

     >>> G=XGraph()

    creates an empty simple and undirected graph (no self-loops or
    multiple edges allowed).  It is equivalent to the expression:

    >>> G=XGraph(name='',selfloops=False,multiedges=False)

    >>> G=XGraph(name="empty",multiedges=True)

    creates an empty graph with G.name="empty", that does not allow 
    the addition of self-loops but does allow for multiple edges.
    
    See also the XDiGraph class.

    =============
    XGraph inherits from Graph, overriding the following methods:

    - __init__
    - add_edge
    - add_edges_from
    - has_edge, has_neighbor
    - get_edge
    - edges_iter
    - delete_edge
    - delete_edges_from
    - degree_iter
    - to_directed
    - copy
    - subgraph

    XGraph adds the following methods to those of Graph:

    - delete_multiedge
    - nodes_with_selfloops
    - selfloop_edges
    - number_of_selfloops
    - allow_selfloops
    - remove_all_selfloops
    - ban_selfloops
    - allow_multiedges
    - remove_all_multiedges
    - ban_multiedges

    """


    def __init__(self, data=None, name='', selfloops=False, multiedges=False):
        """Initialize XGraph.

        Optional arguments::
        name: graph name (default='')
        selfloops: if True selfloops are allowed (default=False)
        multiedges: if True multiple edges are allowed (default=False)

        """
        self.adj={}      # adjacency list
        self.selfloops=selfloops
        self.multiedges=multiedges
        if data is not None:
            self=convert.from_whatever(data,create_using=self)
        self.name=name

    def add_edge(self, n1, n2=None, x=None):  
        """Add a single edge to the graph.

        Can be called as G.add_edge(n1,n2,x) or as
        G.add_edge(e), where e=(n1,n2,x).

        n1,n2 are node objects, and are added to the Graph if not already
        present.  Nodes must be hashable Python objects (except None).

        x is an arbitrary (not necessarily hashable) object associated
        with this edge. It can be used to associate one or more:
        labels, data records, weights or any arbirary objects to
        edges.  The default is the Python None.

        For example, if the graph G was created with

        >>> G=XGraph()

        then G.add_edge(1,2,"blue") will add the edge (1,2,"blue").

        If G.multiedges=False, then a subsequent G.add_edge(1,2,"red")
        will change the above edge (1,2,"blue") into the edge (1,2,"red").

        
        If G.multiedges=True, then two successive calls to
        G.add_edge(1,2,"red") will result in 2 edges of the form
        (1,2,"red") that can not be distinguished from one another.
        
        G.add_edge(1,2,"green") will add both edges (1,2,X) and (2,1,X).

        If self.selfloops=False, then calling add_edge(n1,n1,x) will have no
        effect on the Graph.

        Objects associated to an edge can be retrieved using edges(),
        edge_iter(), or get_edge().

        """
        if n2 is None: # add_edge was called as add_edge(e), with  e=(n1,n2,x)
            if len(n1)==3: # case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1   # x=None

        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(n1,n2,x):
            return

        # add nodes            
        if n1 not in self.adj:
            self.adj[n1]={}
        if n2 not in self.adj:
            self.adj[n2]={}
        
        # self loop? quietly return if not allowed
        if not self.selfloops and n1==n2: 
            return

        if self.multiedges: # add x to the end of the list of objects
                            # that defines the edges between n1 and n2
            self.adj[n1][n2]=self.adj[n1].get(n2,[])+ [x]
            if n1!=n2:
                self.adj[n2][n1]=self.adj[n2].get(n1,[])+ [x]
        else:  # x is the new object assigned to single edge between n1 and n2
            self.adj[n1][n2]=x
            if n1!=n2:
                self.adj[n2][n1]=x # a copy would be required to avoid
                                   # modifying both at the same time
                                   # when doing a delete_edge

    def add_edges_from(self, ebunch):  
        """Add multiple edges to the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2). See add_edge documentation.

        The container must be iterable or an iterator.  It is iterated
        over once.

        """
        for e in ebunch:
            self.add_edge(e)

    def has_edge(self, n1, n2=None, x=None):
        """Return True if graph contains edge (n1,n2,x).

        Can be called as G.has_edge(n1,n2,x)
        or as G.has_edge(e), where e=(n1,n2,x).

        If x is unspecified or None, i.e. if called with an edge of the form
        e=(n1,n2), then return True if there exists ANY edge between
        n1 and n2 (equivalent to has_neighbor(n1,n2))

        """
        if n2 is None:
            # has_edge was called as has_edge(e)
            if len(n1)==3: #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1
                return self.has_neighbor(n1,n2)
        else:
            if x is None:
                # has_edge was called as has_edge(n1,n2)
                # return True if there exists ANY
                # edge between n1 and n2
                return self.has_neighbor(n1,n2)
        # case where x is specified
        if self.multiedges:
            return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2) and
                x in self.adj[n1][n2])
        else:
            return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2) and
                x==self.adj[n1][n2])            


    def has_neighbor(self, n1, n2):
        """Return True if node n1 has neighbor n2.

        Note that this returns True if there exists ANY edge (n1,n2,x)
        for some x.

        """
        return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2))
    
    def neighbors_iter(self, n):
        """Return an iterator of nodes connected to node n. 

        Returns the same data as edges(n) but in a different format.

        """
        if not self.multiedges:
            try:
                for nbr in Graph.neighbors_iter(self,n):
                    yield nbr
            except KeyError:
                raise NetworkXError, "node %s not in graph"%n
        else:
            if n not in self:
                raise NetworkXError, "node %s not in graph"%n
            for (u,v,d) in self.edges_iter(n):
                yield v

    def get_edge_iter(self, u, v):
        """Return an iterator over the objects associated with each edge
        from node u to node v.

        """
        if v is None:
            (u,v)=u
        try:
            result = self.adj[u][v]    # raises KeyError if edge not found
            if self.multiedges:
                for data in result:
                    yield data
            else:
                yield result
        except KeyError:
            pass

    def get_edge(self, u, v):
        """Return the objects associated with each edge from node u to node v.

        If multiedges=False, a single object is returned.
        If multiedges=True, a list of objects is returned.
        If no edge exists, None is returned.

        """
        edge_data=list(self.get_edge_iter(u,v))
        if self.multiedges:
            return edge_data
        else:
            return edge_data[0]
            
            
    def edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all nodes in graph if nbunch=None.

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
        seen={}  # helper dict used to avoid duplicate edges
        if self.multiedges:
            for n1 in bunch:
                for n2,elist in self.adj[n1].iteritems(): 
                    if n2 not in seen:
                        for data in elist:
                            yield (n1,n2,data)
                seen[n1]=1
        else:   
            for n1 in bunch:
                for n2,data in self.adj[n1].iteritems(): 
                    if n2 not in seen:
                        yield (n1,n2,data)
                seen[n1]=1
        del(seen) # clear copy of temp dictionary
               # iterators can remain after they finish returning values.

    def delete_multiedge(self, n1, n2):
        """ Delete all edges between nodes n1 and n2.
     
         When there is only a single edge allowed between nodes
         (multiedges=False), this just calls delete_edge(n1,n2)
         otherwise (multiedges=True) all edges between n1 and n2 are deleted.
         """
        if self.multiedges:
            for x in self.get_edge(n1, n2):
                self.delete_edge(n1, n2, x)
        else:
            self.delete_edge(n1, n2)
        return

    def delete_edge(self, n1, n2=None, x=None): 
        """Delete the edge (n1,n2,x) from the graph.

        Can be called either as

        >>> G.delete_edge(n1,n2,x)
        or
        >>> G.delete_edge(e)

        where e=(n1,n2,x).

        The default edge data is x=None

        If called with an edge e=(n1,n2), or as G.delete_edge(n1,n2)
        then the edge (n1,n2,None) will be deleted.

        If the edge does not exist, do nothing.

        To delete *all* edges between n1 and n2 use
        >>> G.delete_multiedges(n1,n2)
        
        """
        if n2 is None:      # was called as delete_edge(e)
            if len(n1)==3:  # case e=(n1,n2,x)
                n1,n2,x=n1
            else:           # assume e=(n1,n2), x unspecified, set to None
                n1,n2=n1    # x=None

        if self.multiedges:
            if (self.adj.has_key(n1)
                and self.adj[n1].has_key(n2)
                and x in self.adj[n1][n2]):  # if (n1,n2,x) is an edge;
                self.adj[n1][n2].remove(x)  # remove the edge item from list
                if n1!=n2:                   # and if not self loop
                    self.adj[n2][n1].remove(x)  # remove n2->n1 entry
                if len(self.adj[n1][n2])==0: # if last edge between n1 and n2
                    del self.adj[n1][n2]      # was deleted, remove all trace
                    if n1!=n2:                # and if not self loop
                        del self.adj[n2][n1]  # remove n2->n1 entry
        else:  # delete single edge       
            if self.has_neighbor(n1,n2):
                del self.adj[n1][n2]
                if n1!=n2:
                    del self.adj[n2][n1]
        return

    def delete_edges_from(self, ebunch): 
        """Delete edges in ebunch from the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2).  In the latter case all edges
        between n1 and n2 will be deleted. See delete_edge.

        The container must be iterable or an iterator, and
        is iterated over once. Edges that are not in the graph are ignored.

        """
        for e in ebunch:
            # the function-call-in-a-loop cost can be avoided by pasting
            # in the code from delete_edge, do we have a good reason ?
            self.delete_edge(e)

    def degree_iter(self,nbunch=None,with_labels=False):
        """This is the degree() method returned in iterator form.
        If with_labels=True, iterator yields 2-tuples of form (n,degree(n))
        (like iteritems() on a dict.)
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
                deg = sum([len(e) for e in self.adj[n].itervalues()])
                if self.selfloops and self.adj[n].has_key(n):
                    deg+= len(self.adj[n][n])  # double count self-loops 
                if with_labels:
                    yield (n,deg) # tuple (n,degree)
                else:
                    yield deg
        else:
            for n in bunch:
                deg=len(self.adj[n])
                deg+= self.adj[n].has_key(n)  # double count self-loop
                if with_labels:
                    yield (n,deg) # tuple (n,degree)
                else:
                    yield deg

    def copy(self):
        """Return a (shallow) copy of the graph.

        Return a new XGraph with same name and same attributes for
        selfloop and multiededges. Each node and each edge in original
        graph are added to the copy.
                
        """
        H=self.__class__(multiedges=self.multiedges,selfloops=self.selfloops)
        H.name=self.name
        for n in self:
            H.add_node(n)
        for e in self.edges_iter():
            H.add_edge(e)
        return H
        
    def to_directed(self):
        """Return a directed representation of the XGraph G.

        A new XDigraph is returned with the same name, same nodes and
        with each edge (u,v,x) replaced by two directed edges
        (u,v,x) and (v,u,x).
        
        """
        from networkx.xdigraph import XDiGraph
        H=XDiGraph(selfloops=self.selfloops,multiedges=self.multiedges)
        H.name=self.name
        for n in self:
            H.add_node(n)
        for e in self.edges_iter():
            H.add_edge(e[0],e[1],e[2])
            H.add_edge(e[1],e[0],e[2])
        return H

    def nodes_with_selfloops(self):
        """Return list of all nodes having self-loops."""
        if not self.selfloops:
            return []
        else:
            return [n for n in self if self.adj[n].has_key(n)]

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
        if not self.selfloops:
            # nothing to do
            return
        for n in self.adj:
            if self.adj[n].has_key(n):
                del self.adj[n][n]            
 
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
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                self.adj[v][u]=[edgedata]

    def remove_all_multiedges(self):
        # FIXME, write tests
        """Remove multiedges retaining the data from the first edge"""
        if not self.multiedges: # nothing to do
            return
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                if len(edgedata)>1:
                    self.adj[v][u]=[edgedata[0]]

    def ban_multiedges(self):
        """Remove multiedges retaining the data from the first edge.
        Henceforth do not allow multiedges.
        """
        if not self.multiedges: # nothing to do
            return
        self.multiedges=False
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                self.adj[v][u]=edgedata[0]
        
    def subgraph(self, nbunch, inplace=False, create_using=None):
        """Return the subgraph induced on nodes in nbunch.

       nbunch: either a singleton node, a string (which is treated
       as a singleton node), or any non-string iterable or iterator.
       (It can be an iterable or an iterator, e.g. a list,
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

        # Create new graph   
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
        H_adj=H.adj       # store in local variables
        self_adj=self.adj 
        if self.multiedges:
            for n in H:   # create neighbor dict with copy of data list from self
                H_adj[n]=dict([(u,d[:]) for u,d in self_adj[n].iteritems() if u in H_adj])
        else: # no multiedges
            for n in H:   # create neighbor dict with edge data from self
                H_adj[n]=dict([(u,d) for u,d in self_adj[n].iteritems() if u in H_adj])
        return H


    def number_of_edges(self, u=None, v=None, x=None):
        """Return the number of edges between nodes u and v.

        If u and v are not specified return the number of edges in the
        entire graph.

        The edge argument e=(u,v) can be specified as 
        G.number_of_edges(u,v) or G.number_of_edges(e)

        """
        if u is None: return self.size()
        if v is None:
            if len(u)==3: # e=(u,v,x)
                (u,v,x)=u
            else: # assume e=(u,v), x=None
                (u,v)=u
                
        if self.has_edge(u,v,x):
            if self.multiedges:
                if x is None: # return all edges
                    return len(self.get_edge(u,v))
                else: # only edges matching (u,v,x)
                    return len([d for d in self.get_edge(u,v) if d is x])
            else:
                return 1
        else:
            return 0

   

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite(
                                'tests/xgraph_XGraph.txt',
                                'tests/xgraph_XGraph_multiedges_selfloops.txt',
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
    
