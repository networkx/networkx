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
    """A directed graph that allows self-loops, but not multiple 
    (parallel) edges.   

    Edge and node data is the same as for Graph.
    Subclass of Graph.

    An empty digraph is created with

    >>> G=nx.DiGraph()

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
        """Add a node to this digraph.

        If the node n is already in this digraph, then it is (quietly) ignored.

        Parameters
        ----------
        n : node
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        Examples
        --------
        It's very easy to add a new node to a digraph.

        >>> ebunch = [(1, 1), (3, 2)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.nodes()
        [1, 2, 3]
        >>> g.add_node(4)  # add the new node 4
        >>> g.nodes()
        [1, 2, 3, 4]

        One cannot add a node that is already in the digraph.

        >>> ebunch = [(1, 1), (3, 2)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.nodes()
        [1, 2, 3]
        >>> g.add_node(2)  # node 2 already in digraph, so ignore it
        >>> g.nodes()
        [1, 2, 3]

        See Also
        --------
        add_nodes_from : add a bunch of nodes
        """
        if n not in self.succ:
            self.succ[n] = {}
            self.pred[n] = {}

    add_node.__doc__ = Graph.add_node.__doc__.replace('Graph','DiGraph')

    def add_nodes_from(self, nbunch):
        """Add the nodes in nbunch to this digraph.

        If any node in nbunch is already in this digraph, then it is (quietly)
        ignored.

        Parameters
        ----------
        nbunch : list, iterable
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None.

        Examples
        --------
        It's very easy to add new nodes to a digraph.

        >>> ebunch = [(1, 1), (3, 2)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.nodes()
        [1, 2, 3]
        >>> nbunch = [4, 5, 6]  # new nodes to be added
        >>> g.add_nodes_from(nbunch)
        >>> g.nodes()
        [1, 2, 3, 4, 5, 6]

        One cannot add a node that is already in the digraph.

        >>> ebunch = [(1, 1), (3, 2), (1, 4)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.nodes()
        [1, 2, 3, 4]
        >>> nbunch = [4, 5]  # node 4 will be ignored
        >>> g.add_nodes_from(nbunch)
        >>> g.nodes()
        [1, 2, 3, 4, 5]

        See Also
        --------
        add_node : add a single node
        """
        for n in nbunch:
            if n not in self.succ:
                self.succ[n] = {}
                self.pred[n] = {}

    add_nodes_from.__doc__ = \
        Graph.add_nodes_from.__doc__.replace('Graph','DiGraph')


    def remove_node(self, n):
        """Remove the specified node from this digraph.

        Removing the node n from this digraph also has the effect of removing
        any edges having n as a node.

        Parameters
        ----------
        n : node
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.        

        Examples
        --------
        >>> ebunch = [(1, 1), (3, 2), (1, 4), (3, 4)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges(); g.nodes()
        [(1, 1), (1, 4), (3, 2), (3, 4)]
        [1, 2, 3, 4]
        >>> g.remove_node(4)  # edges (1,4) and (3,4) are also removed
        >>> g.edges(); g.nodes()
        [(1, 1), (3, 2)]
        [1, 2, 3]

        See Also
        --------
        remove_nodes_from : remove a bunch of nodes
        """
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
        """Remove all nodes in nbunch from this digraph.

        Removing the nodes in nbunch from this digraph also has the effect of
        removing any edges having those nodes.

        Parameters
        ----------
        nbunch : list, iterable
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None.

        Examples
        --------
        >>> ebunch = [(1, 1), (3, 2), (1, 4), (3, 4), (5, 6)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges(); g.nodes()
        [(1, 1), (1, 4), (3, 2), (3, 4), (5, 6)]
        [1, 2, 3, 4, 5, 6]
        >>> nbunch = [4, 5, 6]  # nodes to be removed
        >>> g.remove_nodes_from(nbunch)  # edges (1,4), (3,4), (5,6) also to be removed
        >>> g.edges(); g.nodes()
        [(1, 1), (3, 2)]
        [1, 2, 3]

        See Also
        --------
        remove_node : remove a single node
        """
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
        """Add a single directed edge (u,v) to the digraph.

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object. The order of
            u and v specifies the direction of the edge. In this case, the
            method adds a directed edge from u to v.

        data : any Python object (default: 1)
            Data can be arbitrary (not necessarily hashable) object associated
            with the edge (u,v). It can be used to associate one or more
            labels, data records, weights or any arbitrary objects to edges.

        Examples
        --------
        >>> g = networkx.DiGraph()
        >>> g.add_edge(1, 2)
        >>> g.add_edge(3, 4, data="some data")
        >>> g.edges()
        [(1, 2), (3, 4)]
        >>> g.edges(data=True)
        [(1, 2, 1), (3, 4, 'some data')]

        The class DiGraph does not allow parallel (multiple) edges between a
        pair of nodes.

        >>> g = networkx.DiGraph()
        >>> g.add_edge("a", "b")
        >>> g.edges(data=True)
        [('a', 'b', 1)]
        >>> g.add_edge("a", "b", "my data")
        >>> g.edges(data=True)
        [('a', 'b', 'my data')]

        See Also
        --------
        add_edges_from : add a bunch of edges
        MultiDiGraph.add_edge : the MultiDiGraph class allows parallel edges
        """
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
        """Add edges in ebunch to the digraph.

        Parameters
        ----------
        ebunch : list, iterable
            A container of edges that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid edge (u,v) where each of u and v
            should be a valid node type, i.e. any hashable type
            except None. If an edge (u,v) in ebunch is already in this digraph,
            then (u,v) will be (quietly) ignored.

        data : any Python object (default: 1)
            Data can be arbitrary (not necessarily hashable) object associated
            with the edge (u,v). It can be used to associate one or more
            labels, data records, weights or any arbitrary objects to edges.

        Examples
        --------
        Adding a bunch of edges to a digraph.

        >>> g = networkx.DiGraph()
        >>> g.edges()
        []
        >>> ebunch = [("a", 1), (2, "b"), ("e", "d")]
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [('a', 1), (2, 'b'), ('e', 'd')]

        Any edges already in the digraph are ignored.

        >>> ebunch = [(1, 1), (3, 2), (1, 4)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 4), (3, 2)]
        >>> mebunch = [(1, 1), (4, 5)]  # edges to add
        >>> g.add_edges_from(mebunch)  # ignore edge (1,1)
        >>> g.edges()
        [(1, 1), (1, 4), (3, 2), (4, 5)]

        See Also
        --------
        add_edge : add a single edge
        """
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
        """Remove the directed edge (u,v).

        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object. The order of
            u and v specifies the direction of the edge. In this case, the
            method removes a directed edge from u to v.

        Examples
        --------
        >>> g = networkx.DiGraph()
        >>> g.add_edge(1, 2)
        >>> g.add_edge(3, 2)
        >>> g.add_edge(4, 2)
        >>> g.edges(data=True)
        [(1, 2, 1), (3, 2, 1), (4, 2, 1)]
        >>> g.remove_edge(1, 2)
        >>> g.edges(data=True)
        [(3, 2, 1), (4, 2, 1)]

        See Also
        --------
        MultiDiGraph.remove_edge : the MultiDiGraph class allows parallel edges
        """
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
        """Return an iterator over the edges.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges in the 
            digraph. Nodes in nbunch that are not in the digraph
            will be (quietly) ignored.

        data : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,data) (True).

        Returns
        --------
        Edges that have nodes in nbunch as start nodes, or a list of all edges
        if nbunch is not specified. If (u,v) is a directed edge of this
        digraph, then u is the start node and v is the end node.

        Examples
        --------
        Get all the edges of a digraph.

        >>> nbunch = [(1, 2), (1, 2, "some data"), (3, 2), (4, 3), (5, 3)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(nbunch)
        >>> list(g.edges_iter())  # get all the edges
        [(1, 2), (3, 2), (4, 3), (5, 3)]
        >>> [e for e in g.edges_iter()]  # another way to get the edges
        [(1, 2), (3, 2), (4, 3), (5, 3)]
        >>> g.edges()  # recommended way to get the edges
        [(1, 2), (3, 2), (4, 3), (5, 3)]

        Get only the specified edges.

        >>> nbunch = [(1, 2), (1, 2, "some data"), (3, 2), (4, 3), (5, 3)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(nbunch)
        >>> g.edges()
        [(1, 2), (3, 2), (4, 3), (5, 3)]
        >>> ebunch = [1, 3]  # get edges with these as start nodes
        >>> list(g.edges_iter(ebunch))
        [(1, 2), (3, 2)]

        See Also
        --------
        in_edges_iter : return an iterator over in-edges
        MultiDiGraph.edges_iter : the MultiDiGraph class allows parallel edges
        """
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
    # alias out_edges to edges
    out_edges_iter=edges_iter
    out_edges=Graph.edges

    def in_edges_iter(self, nbunch=None, data=False):
        """Return an iterator over in-edges.
        
        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once.
            If nbunch is None, return all edges.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        data : bool
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True)

        Returns
        -------
        An iterator over in-edges that are incident to any node in nbunch,
        or over all in-edges if nbunch is not specified.
        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,data in nbrs.iteritems():
                    yield (nbr,n,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr in nbrs:
                    yield (nbr,n)

    def in_edges(self, nbunch=None, data=False):
        """Return a list of in-edges.
        
        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once. If nbunch
            is None, return all in-edges. Nodes in nbunch that are not in the
            graph will be (quietly) ignored.

        data : bool (default: False)
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True)

        Returns
        -------
        A list of in-edges that are incident to any node in nbunch,
        or a list of all in-edges if nbunch is not specified.
        """
        return list(self.in_edges_iter(nbunch, data))

    def degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, degree).

        The node degree is the number of edges adjacent to that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the degree of all
            nodes in the digraph. Nodes in nbunch that are not in the digraph
            will be (quietly) ignored.

        weighted : bool (default: False)
            If the digraph is weighted, return the weighted degree
            (the sum of edge weights).

        Examples
        --------
        Get the degree of all nodes.

        >>> ebunch = [(1, 2), (2, 1, "some data"), (3, 4), (5, 2, "more data")]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.degree_iter())  # get degree of all nodes
        [(1, 2), (2, 3), (3, 1), (4, 1), (5, 1)]
        >>> [d for d in g.degree_iter()]  # another way
        [(1, 2), (2, 3), (3, 1), (4, 1), (5, 1)]

        Only get the degree of specified nodes.

        >>> ebunch = [(1, 2), (2, 1, "some data"), (3, 4), (5, 2, "more data")]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> nbunch = [2, 4]  # get degree of nodes 2, 4
        >>> list(g.degree_iter(nbunch))
        [(2, 3), (4, 1)]

        See Also
        --------
        in_degree_iter : degree iterator for in-edges
        out_degree_iter : degree iterator for out-edges
        MultiDiGraph.degree_iter : the MultiDiGraph class allows parallel edges
        """
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
        """Return an iterator for (node, in-degree).

        The node in-degree is the number of edges pointing in to that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            Any single node or any sequence/iterator of nodes. Each element of
            the container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the in-degree iterator of
            all nodes in the digraph. Nodes in nbunch that are not in the
            digraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the digraph is weighted, return the weighted in-degree
            (the sum of in-edge weights).

        Examples
        ---------
        Get the in-degree iterator of all nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.in_degree_iter())  # get in-degree iterator of all nodes
        [(1, 1), (2, 1), (3, 2), (4, 0)]
        >>> [d for d in g.in_degree_iter()]  # another way
        [(1, 1), (2, 1), (3, 2), (4, 0)]

        Get the in-degree iterator of specified nodes.

        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> list(G.in_degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.in_degree_iter([0,1]))
        [(0, 1), (1, 2)]

        See Also
        --------
        degree_iter : degree iterator for nodes
        out_degree_iter : degree iterator for out-edges
        MultiDiGraph.in_degree_iter : the MultiDiGraph class allows parallel edges
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
        """Return an iterator for (node, out-degree).

        The node degree is the number of edges pointing out of that node. 

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            Any single node or any sequence/iterator of nodes. Each element of
            the container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the out-degree iterator of
            all nodes in the digraph. Nodes in nbunch that are not in the
            digraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the digraph is weighted, return the weighted out-degree
            (the sum of out-edge weights).

        Examples
        ---------
        Get out-degree iterator of all nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.out_degree_iter())  # get out-degree iterator of all nodes
        [(1, 1), (2, 2), (3, 0), (4, 1)]
        >>> [d for d in g.out_degree_iter()]  # another way
        [(1, 1), (2, 2), (3, 0), (4, 1)]

        Get out-degree iterator of specified nodes.

        >>> G=nx.DiGraph(nx.path_graph(4))
        >>> list(G.out_degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.out_degree_iter([0,1]))
        [(0, 1), (1, 2)]

        See Also
        --------
        in_degree_iter : degree iterator for in-edges
        degree_iter : degree iterator for nodes
        MultiDiGraph.out_degree_iter : the MultiDiGraph class allows parallel edges
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
        nbunch : list or container of nodes (default: None)
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return the in-degree of all nodes in the
            digraph. Nodes in nbunch that are not in the digraph will be
            (quietly) ignored.

        with_labels : bool (default: False)
            Return a list of in-degrees (False) or a dictionary of
            in-degrees keyed by node (True).

        weighted : bool (default: False)
            If the digraph is weighted, return the weighted in-degree
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

        See Also
        --------
        out_degree : return the out-degree of a node or nodes
        """
        if with_labels:           # return a dict
            return dict(self.in_degree_iter(nbunch,weighted=weighted))
        elif nbunch in self:      # return a single node
            return self.in_degree_iter(nbunch,weighted=weighted).next()[1]
        else:                     # return a list
            return [d for (n,d) in self.in_degree_iter(nbunch,weighted=weighted)]


    def out_degree(self, nbunch=None, with_labels=False, weighted=False):
        """Return the out-degree of a node or nodes.

        The node out-degree is the number of edges pointing out of that node. 

        Parameters
        ----------
        nbunch : list or container of nodes (default: None)
            Any single node or any sequence/iterator of nodes.  
            If nbunch is None, return the out-degree of all nodes in the
            digraph. Nodes in nbunch that are not in the digraph will be
            (quietly) ignored.

        with_labels : bool (default: False)
            Return a list of out-degrees (False) or a dictionary of
            out-degrees keyed by node (True).

        weighted : bool (default: False)
            If the digraph is weighted, return the weighted out-degree
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

        See Also
        --------
        in_degree : return the in-degree of a node or nodes
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
        """Return the subgraph induced on nodes in nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. Nodes in nbunch that are not in the digraph will be
            (quietly) ignored.

        copy : bool (default: True)
            If True then return a new digraph holding the subgraph.
            Otherwise, the subgraph is created in the original digraph by
            deleting nodes not in nbunch. Warning: this can destroy the
            digraph.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (2, 1), (3, 2), (4, 4)]
        >>> g = networkx.DiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (2, 1), (3, 2), (4, 4)]
        >>> nbunch = [1, 2, 4]
        >>> sg = g.subgraph(nbunch)  # get subgraph induced by nodes 1, 2, 4
        >>> sg.edges()
        [(1, 1), (1, 2), (2, 1), (4, 4)]

        See Also
        --------
        MultiDiGraph.subgraph : the MultiDiGraph class allows parallel edges
        """
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
        if copy:
            H = self.__class__(name="Reverse of (%s)"%self.name)
            H.pred=self.succ.copy()
            H.adj=self.pred.copy()
            H.succ=H.adj
        else:
            self.pred,self.succ=self.succ,self.pred
            self.adj=self.succ
            H=self
        return H

