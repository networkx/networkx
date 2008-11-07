"""
Base class for digraphs.

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
#
class DiGraph(Graph):
    """ A directed graph that allows self-loops, but not multiple 
    (parallel) edges.   

    Edge and node data is the same as for Graph.
    Subclass of Graph.

    An empty digraph is created with

    >>> G=nx.DiGraph()

    DiGraph inherits from the Graph class and overwrites the methods:
    - __init__
    - add_node
    - add_nodes_from
    - remove_node
    - remove_nodes_from
    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - neighbors
    - neighbors_iter
    - edges_iter
    - degree_iter
    - clear
    - subgraph
    - to_undirected
    - to_directed

    In addition DiGraph adds new methods for:
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
    multigraph=False
    directed=True
    def __init__(self, data=None, name='', weighted=True):
        """Initialize an empty directed graph.

        Examples
        --------
        >>> G=nx.DiGraph()
        >>> G=nx.DiGraph(name='my graph')
        >>> G=nx.DiGraph(weighted=False)  # don't assume edge data are weights
        """
        # We store two adjacency lists:
        # the  predecessors of node n are stored in the dict self.pred
        # the successors of node n are stored in the dict self.succ=self.adj
        self.adj = {}  # empty adjacency dictionary
        self.pred = {}  # predecessor
        self.succ = self.adj  # successor
        self.weighted = weighted
        # attempt to load graph with data
        if data is not None:
            convert.from_whatever(data,create_using=self)
        self.name=name

        
    def add_node(self, n):
        if n not in self.succ:
            self.succ[n] = {}
            self.pred[n] = {}

    add_node.__doc__ = Graph.add_node.__doc__.replace('Graph','DiGraph')

    def add_nodes_from(self, nbunch):
        for n in nbunch:
            if n not in self.succ:
                self.succ[n] = {}
                self.pred[n] = {}

    add_nodes_from.__doc__ = \
        Graph.add_nodes_from.__doc__.replace('Graph','DiGraph')


    def remove_node(self, n):
        try:
            nbrs=self.succ[n]
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError, "node %s not in digraph"%(n,)
        for u in nbrs:
            del self.pred[u][n] # remove all edges n-u in digraph
        del self.succ[n]          # remove node from succ
        for u in self.pred[n]:  
            del self.succ[u][n] # remove all edges n-u in digraph
        del self.pred[n]          # remove node from pred

    remove_node.__doc__ = Graph.remove_node.__doc__.replace('Graph','DiGraph')
    delete_node = remove_node        

    def remove_nodes_from(self, nbunch):
        for n in nbunch: 
            try:
                succs=self.succ[n]
                for u in succs:  
                    del self.pred[u][n] # remove all edges n-u in digraph
                del self.succ[n]          # now remove node
                for u in self.pred[n]:  
                    del self.succ[u][n] # remove all edges n-u in digraph
                del self.pred[n]          # now remove node
            except KeyError:
                pass # silent failure on remove

    remove_nodes_from.__doc__ = \
        Graph.remove_nodes_from.__doc__.replace('Graph','DiGraph')
    delete_nodes_from = remove_nodes_from        


    def add_edge(self, u, v, data=1):  
        # add nodes            
        if u not in self.succ: 
            self.succ[u]={}
            self.pred[u]={}
        if v not in self.succ: 
            self.succ[v]={}
            self.pred[v]={}
        # add edge
        self.succ[u][v]=data
        self.pred[v][u]=data

    add_edge.__doc__ = Graph.add_edge.__doc__.replace('Graph','DiGraph')


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
            if u not in self.succ: 
                self.succ[u] = {}
                self.pred[u] = {}
            if v not in self.succ: 
                self.succ[v] = {}
                self.pred[v] = {}
            self.succ[u][v] = d
            self.pred[v][u] = d

    add_edges_from.__doc__ = \
        Graph.add_edges_from.__doc__.replace('Graph','DiGraph')


    def remove_edge(self, u, v): 
        try:
            del self.succ[u][v]   
            del self.pred[v][u]   
        except KeyError: 
            raise NetworkXError("edge %s-%s not in graph"%(u,v))

    remove_edge.__doc__ = Graph.remove_edge.__doc__.replace('Graph','DiGraph')
    delete_edge = remove_edge            


    def remove_edges_from(self, ebunch): 
        for e in ebunch:
            (u,v)=e[:2]  # ignore edge data
            if u in self.succ and v in self.succ[u]:
                del self.succ[u][v]   
                del self.pred[v][u]        

    remove_edges_from.__doc__ = \
        Graph.remove_edges_from.__doc__.replace('Graph','DiGraph')
    delete_edges_from = remove_edges_from            


    def has_successor(self, u, v):
        """Return True if node u has successor v.

        This is true if graph has the edge u->v.
        """
        return (u in self.succ and v in self.succ[u])

    def has_predecessor(self, u, v):
        """Return True if node u has predecessor v.

        This is true if graph has the edge u<-v.
        """
        return (u in self.pred and v in self.pred[u])    

    def successors_iter(self,n):
        """Return an iterator over successor nodes of n."""
        try:
            return self.succ[n].iterkeys()
        except KeyError:
            raise NetworkXError, "node %s not in digraph"%(n,)

    def predecessors_iter(self,n):
        """Return an iterator over predecessor nodes of n."""
        try:
            return self.pred[n].iterkeys()
        except KeyError:
            raise NetworkXError, "node %s not in digraph"%(n,)

    def successors(self, n):
        """Return a list of sucessor nodes of n."""
        return list(self.successors_iter(n))

    def predecessors(self, n):
        """Return a list of predecessor nodes of n."""
        return list(self.predecessors_iter(n))


    # digraph definintions 
    neighbors = successors
    neighbors.__doc__ = Graph.neighbors.__doc__
    neighbors_iter = successors_iter
    neighbors_iter.__doc__ = Graph.neighbors_iter.__doc__
        


    def edges_iter(self, nbunch=None, data=False):
        if nbunch is None:
            nodes_nbrs=self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,data in nbrs.iteritems():
                    yield (n,nbr,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr in nbrs:
                    yield (n,nbr)

    edges_iter.__doc__ = Graph.edges_iter.__doc__   
   

    def degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs=self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of edge weights
            for n,nbrs in nodes_nbrs:
                yield (n,sum(nbrs.itervalues())+sum(self.pred[n].itervalues()))
        else:
            for n,nbrs in nodes_nbrs:
                yield (n,len(nbrs)+len(self.pred[n])) 

    degree_iter.__doc__ = Graph.degree_iter.__doc__

    def in_degree_iter(self, nbunch=None, weighted=False):
        """Return an interator for (node, in degree). 

        The node in degree is the number of edges pointing in to that node. 

        Parameters
        ----------
        nbunch : list or container of nodes
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        ---------
        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> list(G.in_degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.in_degree_iter([0,1]))
        [(0, 1), (1, 2)]
        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of edge weights
            for n,nbrs in nodes_nbrs:
                yield (n,sum(nbrs.itervalues()))
        else:
            for n,nbrs in nodes_nbrs:
                yield (n,len(nbrs))


    def out_degree_iter(self, nbunch=None, weighted=False):
        """Return an interator for (node, out degree). 

        The node degree is the number of edges pointing out of that node. 

        Parameters
        ----------
        nbunch : list or container of nodes
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        ---------
        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> list(G.out_degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.out_degree_iter([0,1]))
        [(0, 1), (1, 2)]
        """
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of edge weights
            for n,nbrs in nodes_nbrs:
                yield (n,sum(nbrs.itervalues()))
        else:
            for n,nbrs in nodes_nbrs:
                yield (n,len(nbrs))


    def in_degree(self, nbunch=None, with_labels=False, weighted=False):
        """Return the in-degree of a node or nodes.

        The node in-degree is the number of edges pointing in to that node. 

        Parameters
        ----------
        nbunch : list or container of nodes
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        with_labels : False|True
            Return a list of degrees (False) or a dictionary of
            degrees keyed by node (True).

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        ---------
        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> G.in_degree(0)
        1
        >>> G.in_degree([0,1])
        [1, 2]
        >>> G.in_degree([0,1],with_labels=True)
        {0: 1, 1: 2}

        """
        if with_labels:           # return a dict
            return dict(self.in_degree_iter(nbunch,weighted=weighted))
        elif nbunch in self:      # return a single node
            return self.in_degree_iter(nbunch,weighted=weighted).next()[1]
        else:                     # return a list
            return [d for (n,d) in self.in_degree_iter(nbunch,weighted=weighted)]


    def out_degree(self, nbunch=None, with_labels=False, weighted=False):
        """Return the in-degree of a node or nodes.

        The node in-degree is the number of edges pointing in to that node. 

        Parameters
        ----------
        nbunch : list or container of nodes
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        with_labels : False|True
            Return a list of degrees (False) or a dictionary of
            degrees keyed by node (True).

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        ---------
        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> G.out_degree(0)
        1
        >>> G.out_degree([0,1])
        [1, 2]
        >>> G.out_degree([0,1],with_labels=True)
        {0: 1, 1: 2}

        """
        if with_labels:           # return a dict
            return dict(self.out_degree_iter(nbunch,weighted=weighted))
        elif nbunch in self:      # return a single node
            return self.out_degree_iter(nbunch,weighted=weighted).next()[1]
        else:                     # return a list
            return [d for (n,d) in self.out_degree_iter(nbunch,weighted=weighted)]


    def clear(self):
        self.name=''
        self.succ.clear() 
        self.pred.clear() 

    clear.__doc__ = Graph.clear.__doc__


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
            H_succ=H.succ       # store in local variables
            H_pred=H.pred       
            self_succ=self.succ 
            self_pred=self.pred 
            for n in bunch:
                H_succ[n]=dict([(u,d) for u,d in self_succ[n].iteritems() 
                                if u in bunch])
                H_pred[n]=dict([(u,d) for u,d in self_pred[n].iteritems() 
                                if u in bunch])
            return H

    subgraph.__doc__ = Graph.subgraph.__doc__


    def to_undirected(self):
        """Return an undirected representation of the digraph.
    
        A new graph is returned with the same name and nodes and
        with edge (u,v,data) if either (u,v,data) or (v,u,data) 
        is in the digraph.  If both edges exist in digraph and
        their edge data is different, only one edge is created
        with an arbitrary choice of which edge data to use.  
        You must check and correct for this manually if desired.
        
        """
        H=Graph()
        H.name=self.name
        H.add_nodes_from(self)
        H.add_edges_from([(v,u,d) for (u,v,d) in self.edges_iter(data=True)])
        return H
    
    def to_directed(self):
        """Return a directed representation of the current graph.

        If the graph is already directed this returns a copy of the
        graph.

        """
        return self.copy()
        

    def reverse(self, copy=True):
        """Return the reverse of the graph
        
        The reverse is a graph with the same nodes and edges
        but with the directions of the edges reversed.
        """
        H = self.__class__(name="Reverse of (%s)"%self.name)
        H.add_nodes_from(self)
        H.add_edges_from([(v,u,d) for (u,v,d) in self.edges_iter(data=True)])
        return H
