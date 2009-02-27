"""
Base class for MultiDiGraph.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2009 by 
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


class MultiDiGraph(MultiGraph,DiGraph):
    """A directed graph that allows multiple (parallel) edges with arbitrary 
    data on the edges.

    Subclass of MultiGraph and DiGraph (which are both subclasses of Graph).

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
    e=(u,v,k), where u and v are (hashable) objects (nodes) and k
    is an arbitrary (and necessarily unique) key associated with
    that edge that edge.  If the key is not specified one will
    be assigned internally.

    The graph is directed and multiple edges between the same nodes are allowed.

    MultiDiGraph inherits all purely node-specific methods from DiGraph
    and some edge methods from MultliGraph.
    MultiDiGraph edges are identical to MultiGraph
    edges, except that they are directed rather than undirected.

    MultiDiGraph replaces the following DiGraph methods:

    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - has_edge
    - get_edge
    - edges_iter
    - degree_iter
    - in_degree_iter
    - out_degree_iter
    - selfloop_edges
    - number_of_selfloops
    - subgraph
    - to_undirected
    
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

    """
    multigraph=True
    directed=True

    def add_edge(self, u, v, data=1, key=None):  
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
            datadict=self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key=0
                while key in datadict:
                    key+=1
            datadict[key]=data
        else:
            # selfloops work this way without special treatment
            if key is None:
                key=0
            datadict={key:data}
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict

    def remove_edge(self, u, v, key=None):
        """Remove the edge between (u,v).

        If data is defined only remove the first edge found with 
        edge data == data.  

        If data is None, remove all edges between u and v.
        """
        if key is None: 
            super(MultiDiGraph,self).remove_edge(u,v)
        else:
            try:
                d=self.adj[u][v]
                # remove the edge with specified data
                del d[key]   
                if len(d)==0:
                    # remove the key entries if last edge
                    del self.succ[u][v]
                    del self.pred[v][u]
            except (KeyError,ValueError): 
                raise NetworkXError(
                    "edge %s-%s with key %s not in graph"%(u,v,key))

    delete_edge = remove_edge            


    def edges_iter(self, nbunch=None, data=False, keys=False):
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (n,nbr,key,data)
                        else:
                            yield (n,nbr,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (n,nbr,key)
                        else:
                            yield (n,nbr)

    # alias out_edges to edges
    out_edges_iter=edges_iter

    def in_edges_iter(self, nbunch=None, data=False, keys=False):
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (nbr,n,key,data)
                        else:
                            yield (nbr,n,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (nbr,n,key)
                        else:
                            yield (nbr,n)

    in_edges_iter.__doc__ = DiGraph.in_edges_iter.__doc__


    def degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                indeg = sum([sum(data.values()) 
                             for data in self.pred[n].itervalues()])
                outdeg = sum([sum(data.values()) 
                              for data in nbrs.itervalues()])
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
                yield (n, sum([sum(data.values()) 
                               for data in nbrs.itervalues()]) )
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
                yield (n, sum([sum(data.values()) 
                               for data in nbrs.itervalues()]) )
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    out_degree_iter.__doc__ = DiGraph.out_degree_iter.__doc__

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
                        data=d.copy() # copy of edge data dict
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
        H.add_edges_from( ((u,v,data,key) 
                           for u,nbrs in self.adjacency_iter() 
                           for v,datadict in nbrs.iteritems() 
                           for key,data in datadict.items()))
        return H
    

    def copy(self):
        """Return a copy of the graph.

        Notes
        -----
        This makes a complete of the graph but does not make copies
        of any underlying node or edge data.  The node and edge data
        in the copy still point to the same objects as in the original.
        """
        H=self.__class__()
        H.name=self.name
        H.succ={}
        H.pred={}
        H.adj=H.succ
        for u,nbrs in self.adjacency_iter():
            H.succ[u]={}
            for v,d in nbrs.iteritems():
                data=d.copy()
                H.succ[u][v]=data
                if not v in H.pred:
                    H.pred[v]={}
                H.pred[v][u]=data
        return H

    to_directed=copy

