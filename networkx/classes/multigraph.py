"""
Base class for MultiGraph.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.classes.graph import Graph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class MultiGraph(Graph):
    """
    An undirected graph that allows multiple (parallel) edges with arbitrary 
    data on the edges.

    Subclass of Graph.

    An empty multigraph is created with

    >>> G=nx.MultiGraph()

    
    Examples
    ========

    Create an empty graph structure (a "null graph") with no nodes and no edges
    
    >>> G=nx.MultiGraph()  

    You can add nodes in the same way as the simple Graph class
    >>> G.add_nodes_from(xrange(100,110))

    You can add edges with data/labels/objects as for the Graph class, 
    but here the same two nodes can have more than one edge between them.

    >>> G.add_edges_from([(1,2,0.776),(1,2,0.535)])

    See also the MultiDiGraph class for a directed graph version.

    MultiGraph inherits from Graph, overriding the following methods:

    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - has_edge
    - edges_iter
    - get_edge
    - degree_iter
    - selfloop_edges
    - number_of_selfloops
    - number_of_edges
    - to_directed
    - subgraph

    """
    multigraph=True
    directed=False

    def add_edge(self, u, v, data=1):  
        if u not in self.adj: 
            self.adj[u] = {}
        if v not in self.adj: 
            self.adj[v] = {}
        datalist = [data]
        if v in self.adj[u]:
            # add data to the list of edgedata between u and v
            self.adj[u][v] += datalist # both directions because same list
        else:
            # selfloops work this way without special treatment
            self.adj[u][v] = datalist 
            self.adj[v][u] = datalist 

    add_edge.__doc__ = Graph.add_edge.__doc__

    def add_edges_from(self, ebunch, data=1):  
        for e in ebunch:
            ne=len(e)
            if ne==3:
                u,v,d = e
            elif ne==2:
                u,v = e  
                d = data
            else: 
                raise NetworkXError,"Edge tuple %s must be a 2-tuple or 3-tuple."%(e,)
            self.add_edge(u,v,d)                

    add_edges_from.__doc__ = Graph.add_edges_from.__doc__

    def remove_edge(self, u, v, data=None):
        """Remove the edge between (u,v).

        If data is defined only remove the first edge found with 
        edge data == data.  

        If data is None, remove all edges between u and v.
        """
        if data is None: 
            super(MultiGraph, self).remove_edge(u,v)
        else:
            try:
                dlist=self.adj[u][v]
                # remove the edge with specified data
                dlist.remove(data)
                if len(dlist)==0: 
                    # remove the key entries if last edge
                    del self.adj[u][v]
                    del self.adj[v][u]
            except (KeyError,ValueError): 
                raise NetworkXError(
                    "edge %s-%s with data %s not in graph"%(u,v,data))

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

    remove_edges_from.__doc__ = Graph.remove_edges_from.__doc__
    delete_edges_from = remove_edges_from            

#    def has_edge(self, u, v, data=None):
#        try:
#            d=self.adj[u][v]
#        except KeyError:
#            return False
#        return data is None or data in d
#
#    has_edge.__doc__ = Graph.has_edge.__doc__

    def edges_iter(self, nbunch=None, data=False):
        seen={}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datalist in nbrs.iteritems():
                    if nbr not in seen:
                        for data in datalist:
                            yield (n,nbr,data)
                seen[n]=1
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datalist in nbrs.iteritems():
                    if nbr not in seen:
                        for data in datalist:
                            yield (n,nbr)
                seen[n] = 1
        del seen

    edges_iter.__doc__ = Graph.edges_iter.__doc__

    def get_edge_data(self, u, v, default=None):
        """Return the data associated with the edge (u,v).

        For multigraphs this returns a list with data for all edges
        (u,v).  Each element of the list is data for one of the 
        edges. 

        Parameters
        ----------
        u,v : nodes

        default:  any Python object            
            Value to return if the edge (u,v) is not found.
            The default is the Python None object.

        Notes
        -----
        It is faster to use G[u][v].

        """
        try:
            return self.adj[u][v]
        except KeyError:
            return default

    def degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                deg = sum([sum(data) for data in nbrs.itervalues()])
                yield (n, deg+(n in nbrs and sum(nbrs[n])))
        else:
            for n,nbrs in nodes_nbrs:
                deg = sum([len(data) for data in nbrs.itervalues()])
                yield (n, deg+(n in nbrs and len(nbrs[n])))

    degree_iter.__doc__ = Graph.degree_iter.__doc__

    def selfloop_edges(self):
        """Return a list of selfloop edges with data (3-tuples)."""
        return [ (n,n,d) 
                 for n,nbrs in self.adj.iteritems() 
                 if n in nbrs for d in nbrs[n]]


    def number_of_selfloops(self):
        """Return the number of selfloop edges counting multiple edges."""
        return len(self.selfloop_edges())


    def number_of_edges(self, u=None, v=None):
        if u is None: return self.size()
        try:
            edgedata=self.adj[u][v]
        except KeyError:
            return 0 # no such edge
        return len(edgedata)

    number_of_edges.__doc__ = Graph.number_of_edges.__doc__

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
            # add edges
            H_adj = H.adj # cache
            self_adj = self.adj # cache
            for n in bunch:
                H_adj[n] = dict([(u,d[:]) for u,d in self_adj[n].iteritems() 
                                 if u in bunch])
            return H

    subgraph.__doc__ = Graph.subgraph.__doc__

    def to_directed(self):
        """Return a directed representation of the graph.
 
        A new multidigraph is returned with the same name, same nodes and
        with each edge (u,v,data) replaced by two directed edges
        (u,v,data) and (v,u,data).
        
        """
        from networkx import MultiDiGraph 
        G=MultiDiGraph()
        G.add_nodes_from(self)
        G.add_edges_from( ((u,v,data) for u,nbrs in self.adjacency_iter() \
                for v,datalist in nbrs.iteritems() for data in datalist) )
        return G

