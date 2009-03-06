"""
Base class for MultiGraph.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.classes.graph import Graph
from networkx import NetworkXException, NetworkXError
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

    To distinguish between two edges connecting the same nodes you
    can use a key attribute
    
    >>> G.add_edge(1,2,data=0.7,key='first')
    >>> G.add_edge(1,2,data=0.8,key='second')

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
    - copy

    """
    multigraph=True
    directed=False

    def add_edge(self, u, v, data=1, key=None):
        """Add an edge between u and v with optional data and key.

        If the nodes u and v are not already in the multigraph, they will be
        automatically added.

        Parameters                                                      
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        data : any hashable Python object (default: 1)
            Data on an edge can be any arbitrary Python object.

        key : any hashable Python object (default: None)
            A key associated with an edge can be any arbitrary Python object.
            It is used for distinguishing between edges with the same nodes. If
            more than one edge share the same pair of nodes, then the keys
            associated with those edges must each be unique.

        Examples
        --------
        The following add multiple edges to the same pair of nodes. Each edge
        has arbitrary data and a unique key.

        >>> g = networkx.MultiGraph()
        >>> g.add_edge(1, 2)
        >>> g.add_edge(1, 2, data="arbitrary data")
        >>> g.add_edge(1, 2, data="more arbitrary data", key="specified key")
        >>> g.edges()
        [(1, 2), (1, 2), (1, 2)]
        >>> g.edges(data=True)
        [(1, 2, 1), (1, 2, 'arbitrary data'), (1, 2, 'more arbitrary data')]
        >>> g.edges(keys=True)
        [(1, 2, 0), (1, 2, 1), (1, 2, 'specified key')]
        >>> g.edges(data=True, keys=True)
        [(1, 2, 0, 1), (1, 2, 1, 'arbitrary data'), (1, 2, 'specified key', 'more arbitrary data')]

        See Also
        --------
        add_edges_from : add a collection of edges
        Graph.add_edge : the Graph class does *not* allow parallel edges
        """
        if u not in self.adj: 
            self.adj[u] = {}
        if v not in self.adj: 
            self.adj[v] = {}
        if v in self.adj[u]:
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
            self.adj[u][v] = datadict
            self.adj[v][u] = datadict

#    add_edge.__doc__ = Graph.add_edge.__doc__

    def add_edges_from(self, ebunch, data=1):
        """Add all the edges in ebunch.

        Parameters                                                      
        ----------
        ebunch : list or container of edges
            The container must be iterable or an iterator. It is iterated
            over once. Adding the same edges is in effect creating parallel
            edges between a pair of nodes. The edges in ebunch must be
            2-tuples (u,v), 3-tuples (u,v,d) or 4-tuples (u,v,d,k).

        data : any hashable Python object (default: 1)
            Data on an edge can be any arbitrary Python object.

        Examples
        --------
        >>> edgeBunch = [(1, 2), (1, 2, "arbitrary data"), (1, 2, "more arbitrary data", "specified key")]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(edgeBunch)
        >>> g.edges()
        [(1, 2), (1, 2), (1, 2)]
        >>> g.edges(data=True)
        [(1, 2, 1), (1, 2, 'arbitrary data'), (1, 2, 'more arbitrary data')]
        >>> g.edges(keys=True)
        [(1, 2, 0), (1, 2, 1), (1, 2, 'specified key')]
        >>> g.edges(data=True, keys=True)
        [(1, 2, 0, 1), (1, 2, 1, 'arbitrary data'), (1, 2, 'specified key', 'more arbitrary data')]

        See Also
        --------
        add_edge : add a single edge
        Graph.add_edges_from : the Graph class does *not* allow parallel edges
        """
        for e in ebunch:
            ne=len(e)
            if ne==4:
                u,v,d,k = e                
            elif ne==3:
                u,v,d = e
                k=None
            elif ne==2:
                u,v = e  
                d = data
                k=None
            else: 
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            self.add_edge(u,v,data=d,key=k)                

#    add_edges_from.__doc__ = Graph.add_edges_from.__doc__

    def remove_edge(self, u, v, key=None):
        """Remove the edge between u and v.

        If key is not specified, remove all edges between u and v.

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        key : any hashable Python object (default: None)
            A key associated with an edge can be any arbitrary Python object.
            It is used for distinguishing between edges with the same nodes. If
            more than one edge share the same pair of nodes, then the keys
            associated with those edges must each be unique.

        Examples
        --------
        >>> g = networkx.MultiGraph()
        >>> eBunch = [(1, 2), (1, 2, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key")]
        >>> g.add_edges_from(eBunch)
        >>> g.edges()
        [(1, 2), (1, 2), (1, 2), (3, 4)]
        >>> g.remove_edge(1, 2)
        >>> g.edges()
        [(3, 4)]

        Notes
        -----
        Will fail silently if the edge (u,v) is not in this multigraph.

        See Also
        --------
        remove_edges_from : remove a collection of edges
        Graph.remove_edge : the Graph class does *not* allow parallel edges
        """
        if key is None: 
            super(MultiGraph, self).remove_edge(u,v)
        else:
            try:
                d=self.adj[u][v]
                # remove the edge with specified data
                del d[key]
                if len(d)==0: 
                    # remove the key entries if last edge
                    del self.adj[u][v]
                    del self.adj[v][u]
            except (KeyError,ValueError): 
                raise NetworkXError(
                    "edge %s-%s with key %s not in graph"%(u,v,key))

    delete_edge = remove_edge            

    def remove_edges_from(self, ebunch):
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            A container of edge 2-tuples (u,v) or edge 3-tuples(u,v,k). If an
            edge 2-tuple (u,v) is specified in ebunch, all parallel edges (u,v)
            are removed from this multigraph. Where an edge 3-tuple (u,v,k) is
            among the list of edges to be removed, only the edge (u,v) with
            unique key k will be removed.

        Examples
        --------
        We can remove all parallel edges of a pair of nodes.

        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]
        >>> rbunch = [(1, 2), (1, 4)]
        >>> g.remove_edges_from(rbunch)
        >>> g.edges()
        [(1, 3), (3, 4)]

        If a pair of nodes has parallel edges, we can specify which of those
        edges to remove.

        >>> g = networkx.MultiGraph()
        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]
        >>> rbunch = [(1, 2, "specified key"), (1, 4)]
        >>> g.remove_edges_from(rbunch)
        >>> g.edges()
        [(1, 2), (1, 3), (3, 4)]

        Notes
        -----
        Will fail silently if the edge (u,v) is not in this multigraph.

        See Also
        --------
        remove_edge : remove a single edge
        Graph.remove_edges_from : the Graph class does *not* allow parallel edges
        """
        for e in ebunch:
            u,v = e[:2]
            if u in self.adj and v in self.adj[u]:
                try:
                    key=e[2]
                except IndexError:
                    key=None
                self.remove_edge(u,v,key=key)

#    remove_edges_from.__doc__ = Graph.remove_edges_from.__doc__
    delete_edges_from = remove_edges_from            

    def has_edge(self, u, v, key=None):
        """Return True if the edge (u,v) is in the graph, False otherwise. 

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        key : any hashable Python object (default: None)
            A key associated with an edge can be any arbitrary Python object.
            It is used for distinguishing between edges with the same nodes. If
            more than one edge share the same pair of nodes, then the keys
            associated with those edges must each be unique.
            
        See Also
        --------
        Graph.has_neighbor()

        Examples
        --------
        Can be called either using two nodes u and v, edge 2-tuple (u,v), or
        edge and key 3-tuple (u,v,k).

        >>> g = networkx.MultiGraph()
        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g.add_edges_from(ebunch)
        >>> g.has_edge(1,3)
        True
        >>> e = (1, 2)
        >>> g.has_edge(*e)
        True
        >>> e = (3, 4, "another key")
        >>> g.has_edge(*e)
        True

        The following syntax are all equivalent: 

        >>> g.has_neighbor(1, 2)
        True
        >>> g.has_edge(1, 2)
        True
        >>> 2 in g[1]
        True
        """
        try:
            if key is None:
                return v in self.adj[u]
            else:
                return key in self.adj[u][v]
        except KeyError:
            return False

#    has_edge.__doc__ = Graph.has_edge.__doc__

    def edges(self, nbunch=None, data=False, keys=False):
        """Return a list of edges.

        Parameters
        ----------
        nbunch : list, iterable
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges in the multigraph.
            Nodes in nbunch that are not in the multigraph will be (quietly)
            ignored.

        data : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,data) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        keys : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,key) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        Returns
        --------
        Edges that are adjacent to any node in nbunch, or a list of all edges
        if nbunch is not specified.

        Examples
        --------
        Get all edges in a multigraph.

        >>> g = networkx.MultiGraph() 
        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]

        All edges with data.

        >>> g.edges(data=True)  # default edge data is 1
        [(1, 2, 1), (1, 2, 'more arbitrary data'), (1, 3, 'arbitrary data'), (1, 4, 1), (3, 4, 'too much data')]

        All edges with keys.

        >>> g.edges(keys=True)
        [(1, 2, 0), (1, 2, 'specified key'), (1, 3, 0), (1, 4, 0), (3, 4, 'another key')]

        All edges with data and keys.

        >>> g.edges(data=True, keys=True)  # default edge data is 1
        [(1, 2, 0, 1), (1, 2, 'specified key', 'more arbitrary data'), (1, 3, 0, 'arbitrary data'), (1, 4, 0, 1), (3, 4, 'another key', 'too much data')]

        See Also
        --------
        edges_iter : return an iterator over the edges
        Graph.edges_iter : the Graph class does *not* allow parallel edges
        """
        return list(self.edges_iter(nbunch, data=data,keys=keys))

    def edges_iter(self, nbunch=None, data=False, keys=False):
        """Return an iterator over the edges.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges in the multigraph.
            Nodes in nbunch that are not in the multigraph will be (quietly)
            ignored.

        data : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,data) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        keys : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,key) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        Returns
        --------
        Edges that are adjacent to any node in nbunch, or a list of all edges
        if nbunch is not specified.

        Examples
        --------
        Get all edges in a multigraph.

        >>> g = networkx.MultiGraph()
        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g.add_edges_from(ebunch)
        >>> g.edges()  # recommended way of getting all edges
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]
        >>> [e for e in g.edges_iter()]  # another way to get all edges
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]
        >>> list(g.edges_iter())  # still another way to get all edges
        [(1, 2), (1, 2), (1, 3), (1, 4), (3, 4)]

        See Also
        --------
        edges : return a list of edges
        Graph.edges_iter : the Graph class does *not* allow parallel edges
        """
        seen={}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    if nbr not in seen:
                        for key,data in datadict.iteritems():
                            if keys:
                                yield (n,nbr,key,data)
                            else:
                                yield (n,nbr,data)
                seen[n]=1
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    if nbr not in seen:
                        for key,data in datadict.iteritems():
                            if keys:
                                yield (n,nbr,key)
                            else:
                                yield (n,nbr)

                seen[n] = 1
        del seen

#    edges_iter.__doc__ = Graph.edges_iter.__doc__

    def get_edge_data(self, u, v, key=None, default=None):
        """Return the data associated with the edge (u,v).

        For multigraphs, this returns a list with data for all edges
        (u,v).  Each element of the list is data for one of the 
        edges. 

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        key : any hashable Python object (default: None)
            A key associated with an edge can be any arbitrary Python object.
            It is used for distinguishing between edges with the same nodes. If
            more than one edge share the same pair of nodes, then the keys
            associated with those edges must each be unique.

        default: any hashable Python object (default: None)
            Value to return if the edge (u,v) is not found.

        See Also
        --------
        Graph.get_edge_data : the Graph class does *not* allow parallel edges

        Examples
        --------
        >>> g = networkx.MultiGraph()
        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g.add_edges_from(ebunch)
        >>> g.get_edge_data(1, 2)
        {0: 1, 'specified key': 'more arbitrary data'}
        >>> g.get_edge_data(1, 2, key=0)
        1
        >>> g.get_edge_data(1, 2, key="specified key")
        'more arbitrary data'

        Notes
        -----
        It is faster to use g[u][v].

        >>> g[1][2]
        {0: 1, 'specified key': 'more arbitrary data'}
        """
        try:
            if key is None:
                return self.adj[u][v]
            else:
                return self.adj[u][v][key]
        except KeyError:
            return default

    def degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, degree).

        The node degree is the number of edges adjacent to that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return degree iterator of all
            nodes in the multigraph. Nodes in nbunch that are not in the
            multigraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the multigraph is weighted, return the weighted degree
            (the sum of edge weights).

        Examples
        --------
        Get the degree iterator through all nodes.

        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.degree_iter())  # get degree iterator through all nodes
        [(1, 4), (2, 2), (3, 2), (4, 2)]
        >>> [d for d in g.degree_iter()]  # another way
        [(1, 4), (2, 2), (3, 2), (4, 2)]

        Only get degree iterator through specified nodes.

        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> nbunch = [1, 3, 5]  # get degree iterator through nodes 1, 3, 5
        >>> list(g.degree_iter(nbunch))
        [(1, 4), (3, 2)]

        See Also
        --------
        Graph.degree_iter : the Graph class does *not* allow parallel edges
        """
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

#    degree_iter.__doc__ = Graph.degree_iter.__doc__

    def selfloop_edges(self, data=False):
        """Return a list of selfloop edges.

        Parameters
        ----------
        data : bool (default: False)
            If True then return the selfloop edges together with their edge
            data (if any); otherwise return the 2-tuples that make up selfloop
            edges.

        Returns
        -------
        A list of selfloop edges together with (optionally) their data,
        if any. An empty list is returned if the multigraph has no selfloop
        edges.

        Examples
        --------
        Selfloop edges of a multigraph together with edge data (if any).

        >>> ebunch = [(1, 1), (1, 3, "arbitrary data"), (1, 1, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.selfloop_edges()
        [(1, 1), (1, 1)]
        >>> g.selfloop_edges(data=True)
        [(1, 1, 1), (1, 1, 'more arbitrary data')]

        Return an empty list if the multigraph has no selfloop edges.

        >>> ebunch = [(1, 2), (1, 3, "arbitrary data"), (1, 2, "more arbitrary data", "specified key"), (3, 4, "too much data", "another key"), (1, 4)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.selfloop_edges()
        []

        See Also
        --------
        Graph.selfloop_edges : the Graph class does *not* permit parallel edges
        """
        if data:
            return [ (n,n,d) 
                     for n,nbrs in self.adj.iteritems() 
                     if n in nbrs for d in nbrs[n].values()]
        else:
            return [ (n,n)
                     for n,nbrs in self.adj.iteritems() 
                     if n in nbrs for d in nbrs[n].values()]



    def number_of_selfloops(self):
        """Return the number of selfloop edges counting multiple edges.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2, "some data"), (3, 2), (4, 4), (4, 4, "more data")]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.number_of_selfloops()
        3

        See Also
        --------
        Graph.number_of_selfloops : the Graph class does *not* allow parallel edges
        """
        return len(self.selfloop_edges())


    def number_of_edges(self, u=None, v=None):
        """Return the number of edges between two nodes.

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2, "some data"), (3, 2), (4, 2)]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.number_of_edges()
        5
        >>> g.number_of_edges(1, 2)
        2

        See Also
        --------
        Graph.size : number of edges or option for sum of all edge weights
        Graph.number_of_edges : the Graph class does *not* permit parallel edges
        """
        if u is None: return self.size()
        try:
            edgedata=self.adj[u][v]
        except KeyError:
            return 0 # no such edge
        return len(edgedata)

    number_of_edges.__doc__ = Graph.number_of_edges.__doc__

    def subgraph(self, nbunch, copy=True):
        """Return the subgraph induced on nodes in nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges data in the
            multigraph. Nodes in nbunch that are not in the multigraph will be
            (quietly) ignored.

        copy : bool (default: True)
            If True then return a new multigraph holding the subgraph.
            Otherwise, the subgraph is created in the original multigraph by
            deleting nodes not in nbunch. Warning: this can destroy the
            multigraph.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2, "some data"), (3, 2), (4, 4), (4, 4, "more data")]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3), (4, 4), (4, 4)]
        >>> nbunch = [1, 2, 3]
        >>> sg = g.subgraph(nbunch)  # get subgraph induced by nodes 1, 2, 3
        >>> sg.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3)]

        See Also
        --------
        Graph.subgraph : the Graph class does *not* allow parallel edges
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
            H_adj = H.adj # cache
            self_adj = self.adj # cache
            for n in bunch:
                H_adj[n] = dict([(u,d.copy()) 
                                 for u,d in self_adj[n].iteritems() 
                                 if u in bunch])
            return H

    subgraph.__doc__ = Graph.subgraph.__doc__

    def to_directed(self):
        """Return a directed representation of the graph.

        A new multidigraph is returned with the same name, same nodes and
        with each edge (u,v,data) replaced by two directed edges
        (u,v,data) and (v,u,data).

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2, "some data"), (3, 2), (4, 4), (4, 4, "more data")]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3), (4, 4), (4, 4)]
        >>> g.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3), (4, 4), (4, 4)]
        >>> dig = g.to_directed()  # get a directed representation of g
        >>> dig.edges()
        [(1, 1), (1, 2), (1, 2), (2, 1), (2, 1), (2, 3), (3, 2), (4, 4), (4, 4)]

        See Also
        --------
        Graph.to_directed : the Graph class does *not* allow parallel edges
        """
        from multidigraph import MultiDiGraph
        G=MultiDiGraph()
        G.add_nodes_from(self)
        G.add_edges_from( ((u,v,data,key) 
                           for u,nbrs in self.adjacency_iter() 
                           for v,datadict in nbrs.iteritems() 
                           for key,data in datadict.items()))
        return G

    def copy(self):
        """Return a copy of the graph.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2, "some data"), (3, 2), (4, 4, "more data")]
        >>> g = networkx.MultiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3), (4, 4)]
        >>> h = g.copy()
        >>> h.edges()
        [(1, 1), (1, 2), (1, 2), (2, 3), (4, 4)]
        >>> h == g
        False

        Notes
        -----
        This makes a complete copy of the multigraph but does not make copies
        of any underlying node or edge data.  The node and edge data in the
        copy still point to the same objects as in the original.

        See Also
        --------
        Graph.copy : the Graph class does *not* allow parallel edges
        """
        H=self.__class__()
        H.name=self.name
        H.adj={}
        for u,nbrs in self.adjacency_iter():
            H.adj[u]={}
            for v,d in nbrs.iteritems():
                H.adj[u][v]=d.copy()
        return H



if __name__ == '__main__':

    G=MultiGraph()
    G.add_edge(1,2) 
    G.add_edge(1,2,'data0')
    G.add_edge(1,2,data='data1',key='key1')
    G.add_edge(1,2,'data2','key2')
    print G.edges()
    print G.edges(data=True)
    print G.edges(keys=True)
    print G.edges(data=True,keys=True)
    print G[1][2]
    print G[1][2]['key1']
    G[1][2]['key1']='spam' # OK to set here
    print G[1][2]['key1']
    print G.edges(data=True)
    print G[1][2].keys()
