"""
Base class for MultiDiGraph.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.classes.graph import Graph  # for doctests
from networkx.classes.digraph import DiGraph
from networkx.classes.multigraph import MultiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class MultiDiGraph(DiGraph):
    """A directed graph that allows multiple (parallel) edges with arbitrary 
    data on the edges.

    Subclass of DiGraph which is a subclass of Graph.

    An empty multidigraph is created with

    >>> G=nx.MultiDiGraph()

    Examples
    ========

    Create an empty graph structure (a "null graph") with no nodes and no edges

    >>> G=nx.MultiDiGraph()  

    You can add nodes in the same way as the simple Graph class
    >>> G.add_nodes_from(xrange(100,110))

    You can add edges with data/labels/objects as for the Graph class, 
    but here the same two nodes can have more than one edge between them.

    >>> G.add_edges_from([(1,2,0.776),(1,3,0.535)])

    For graph coloring problems, one could use
    >>> G.add_edges_from([(1,2,"blue"),(1,3,"red")])


    A MultiDiGraph edge is uniquely specified by a 3-tuple
    e=(u,v,x), where u and v are (hashable) objects (nodes) and x
    is an arbitrary (and not necessarily unique) object associated with
    that edge.

    The graph is directed and multiple edges between the same nodes are allowed.

    MultiDiGraph inherits from DiGraph, with all purely node-specific methods
    identical to those of DiGraph. MultiDiGraph edges are identical to MultiGraph
    edges, except that they are directed rather than undirected.

    MultiDiGraph replaces the following DiGraph methods:

    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - get_edge
    - edges_iter
    - degree_iter
    - in_degree_iter
    - out_degree_iter
    - selfloop_edges
    - number_of_selfloops
    - subgraph
    - to_undirected
    
    While MultiDiGraph does not inherit from MultiGraph, we compare them here.
    MultiDigraph adds the following methods to those of MultiGraph:

    - has_successor
    - has_predecessor
    - successors
    - predecessors
    - successors_iter
    - predecessors_iter
    - in_degree
    - out_degree
    - in_degree_iter
    - out_degree_iter
    - reverse

    """
    multigraph=True
    directed=True

    def add_edge(self, u, v, data=1):  
        """Add a single directed edge to the digraph.

        x is an arbitrary (not necessarily hashable) object associated
        with this edge. It can be used to associate one or more,
        labels, data records, weights or any arbirary objects to
        edges. The default is the Python None.

        For example, after creation, the edge (1,2,"blue") can be added

        >>> G=nx.MultiDiGraph()
        >>> G.add_edge(1,2,"blue")

        Two successive calls to G.add_edge(1,2,"red") 
        will result in 2 edges of the form (1,2,"red") 
        that can not be distinguished from one another.

        """
        # add nodes            
        if u not in self.succ: 
            self.succ[u] = {}
            self.pred[u] = {}
        if v not in self.succ: 
            self.succ[v] = {}
            self.pred[v] = {}
        # add data to the list of edgedata between u and v
        datalist = [data]
        if v in self.succ[u]:
            # add data to the list of edgedata between u and v
            self.succ[u][v] += datalist 
        else:
            # selfloops work this way without special treatment
            self.succ[u][v] = datalist 
            self.pred[v][u] = datalist 

    def add_edges_from(self, ebunch, data=1):  
        for e in ebunch:
            ne = len(e)
            if ne==3:
                u,v,d = e
            elif ne==2:
                u,v = e
                d = data
            else: 
                raise NetworkXError,"Edge tuple %s must be a 2-tuple or 3-tuple."%(e,)
            self.add_edge(u,v,d)                

    add_edges_from.__doc__ = DiGraph.add_edges_from.__doc__

    def remove_edge(self, u, v, data=None):
        """Remove edge between (u,v).

        If d is defined only remove the first edge found with 
        edgedata == d.  

        If d is None, remove all edges between u and v.
        """
        if data is None: 
            super(MultiDiGraph,self).remove_edge(u,v)
        else:
            try:
                dlist=self.succ[u][v]
                if d in dlist:
                    dlist.remove(d)
                if len(dlist)==1:
                    # remove the key entries if last edge
                    del self.succ[u][v]
                    del self.pred[v][u]
            except KeyError: 
                raise NetworkXError("edge %s-%s not in graph"%(u,v))

    delete_edge = remove_edge            

    def remove_edges_from(self, ebunch): 
        for e in ebunch:
            u,v = e[:2]
            if u in self.adj and v in self.adj[u]:
                try:
                    data=e[2]
                except IndexError:
                    data=None
                self.remove_edge(u,v,data)

    remove_edges_from.__doc__ = DiGraph.remove_edges_from.__doc__
    delete_edges_from = remove_edges_from            

    def get_edge(self, u, v, no_edge=None):
        """Return a list of edge data for all edges between u and v.

        If no_edge is specified and the edge (u,v) isn't found,
        (and u and v are nodes), return the value of no_edge.  
        If no_edge is None (or u or v aren't nodes) raise an exception.

        """
        try:
            return self.adj[u][v][:]
        except KeyError:
            if no_edge is not None and u in self and v in self: return no_edge
            raise NetworkXError, "edge (%s,%s) not in graph"%(u,v)


    def edges_iter(self, nbunch=None, data=False):
        if nbunch is None:
            nodes_nbrs=self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datalist in nbrs.iteritems():
                    for data in datalist:
                        yield (n,nbr,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datalist in nbrs.iteritems():
                    for data in datalist:
                        yield (n,nbr)

    edges_iter.__doc__ = DiGraph.edges_iter.__doc__

    def degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                indeg = sum([sum(data) for data in self.pred[n].itervalues()])
                outdeg = sum([sum(data) for data in nbrs.itervalues()])
                yield (n, indeg + outdeg  # double counted selfloop so subtract
                       - (n in nbrs and sum(nbrs[n])))
        else:
            for n,nbrs in nodes_nbrs:
                indeg = sum([len(data) for data in self.pred[n].itervalues()])
                outdeg = sum([len(data) for data in nbrs.itervalues()])
                yield (n, indeg + outdeg  # double counted selfloop so subtract
                       - (n in nbrs and len(nbrs[n])))

    degree_iter.__doc__ = DiGraph.degree_iter.__doc__

    def in_degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                yield (n, sum([sum(data) for data in nbrs.itervalues()]) )
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    in_degree_iter.__doc__ = DiGraph.in_degree_iter.__doc__

    def out_degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                yield (n, sum([sum(data) for data in nbrs.itervalues()]) )
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    out_degree_iter.__doc__ = DiGraph.out_degree_iter.__doc__


    def selfloop_edges(self):
        """Return a list of selfloop edges with data (3-tuples)."""
        return [ (n,n,d) 
                 for n,nbrs in self.adj.iteritems() 
                 if n in nbrs for d in nbrs[n]]


    def number_of_selfloops(self):
        """Return the number of selfloop edges counting multiple edges."""
        return len(self.selfloop_edges())

    def subgraph(self, nbunch, copy=True):
        bunch = set(self.nbunch_iter(nbunch))
        if not copy: 
            # demolish all nodes (and attached edges) not in nbunch
            self.remove_nodes_from([n for n in self if n not in bunch])
            self.name = "Subgraph of (%s)"%(self.name)
            return self
        else:
            # create new graph and copy subgraph into it       
            H = self.__class__()
            H.name = "Subgraph of (%s)"%(self.name)
            H.add_nodes_from(bunch)
            # add edges
            H_succ=H.succ       # store in local variables
            H_pred=H.pred       
            self_succ=self.succ 
            self_pred=self.pred 
            for n in bunch:
                for u,d in self_succ[n].iteritems():
                    if u in bunch:
                        data=d[:] # copy of edge list
                        H_succ[n][u]=data
                        H_pred[u][n]=data
            return H

    subgraph.__doc__ = DiGraph.subgraph.__doc__


    def to_undirected(self):
        """Return an undirected representation of the digraph.
    
        A new graph is returned with the same name and nodes and
        with edge (u,v,data) if either (u,v,data) or (v,u,data) 
        is in the digraph.  If both edges exist in digraph they 
        appear as a double edge in the new multigraph.
        
        """
        H=MultiGraph()
        H.name=self.name
        H.add_nodes_from(self)
        H.add_edges_from([(v,u,d) for (u,v,d) in self.edges_iter(data=True)])
        return H
