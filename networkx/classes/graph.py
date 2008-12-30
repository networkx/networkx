"""

Base class for undirected graphs.

The Graph class allows any hashable object as a node 
and can associate any object with an undirected edge.
Self-loops are allowed but multiple edges are not (see MultiGraph)
For directed graphs see DiGraph and XDiGraph.


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#
__docformat__ = "restructuredtext en"

from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class Graph(object):
    """
    An undirected graph class without multiple (parallel) edges.

    Nodes can be arbitrary (hashable) objects.  

    Arbitrary data/labels/objects can be associated with edges.
    The default data is 1.  See add_edge and add_edges_from methods
    for details.  Many NetworkX routines developed for weighted graphs
    assume this data is a number.  Feel free to put other objects on
    the edges, but be aware that these weighted graph algorithms may
    give unpredictable results if the graph isn't a weighted graph.

    Self loops are allowed.

    Examples
    ========

    Create an empty graph structure (a "null graph") with no nodes and 
    no edges.

    >>> import networkx as nx
    >>> G=nx.Graph()

    G can be grown in several ways.
    By adding one node at a time:

    >>> G.add_node(1)

    by adding a list of nodes:

    >>> G.add_nodes_from([2,3])

    by using an iterator:

    >>> G.add_nodes_from(xrange(100,110))

    or by adding any container of nodes (a list, dict, set
    or even a file or the nodes from another graph).

    >>> H=nx.path_graph(10)
    >>> G.add_nodes_from(H)

    Any hashable object (except None) can represent a node, 
    e.g. a customized node object, or even another Graph.

    >>> G.add_node(H)

    G can also be grown by adding one edge at a time:

    >>> G.add_edge(1, 2)

    by adding a list of edges: 

    >>> G.add_edges_from([(1,2),(1,3)])

    or by adding any collection of edges:
    
    >>> G.add_edges_from(H.edges())

    Nodes will be added as needed when you add edges and there are
    no complaints when adding existing nodes or edges.

    The default edge data is the number 1.  
    To add edge information with an edge, use a 3-tuple (u,v,d).

    >>> G.add_edges_from([(1,2,'blue'),(2,3,3.1)])
    >>> G.add_edges_from( [(3,4),(4,5)], data='red')
    >>> G.add_edge( 1, 2, 4.7 )

    """
    multigraph = False
    directed = False
    def __init__(self, data=None, name='', weighted=True):
        """Initialize an empty graph.

        Examples
        --------
        >>> G=nx.Graph()
        >>> G=nx.Graph(name='my graph')
        >>> G=nx.Graph(weighted=False)  # don't assume edge data are weights
        """
        self.adj = {}  # empty adjacency hash
        self.weighted = weighted
        # attempt to load graph with data
        if data is not None:
            convert.from_whatever(data,create_using=self)
        self.name = name

    def __str__(self):
        """Return the name."""
        return self.name

    def __iter__(self):
        """Iterate over the nodes. Use "for n in G".

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print [n for n in G]
        [0, 1, 2, 3]

        """
        return self.adj.iterkeys()

    def __contains__(self,n):
        """Return True if n is a node, False otherwise. Use "n in G".

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print 1 in G
        True
        """
        try:
            return n in self.adj
        except TypeError:
            return False
        
    def __len__(self):
        """Return the number of nodes. Use "len(G)".

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print len(G)
        4

        """
        return len(self.adj)

    def __getitem__(self, n):
        """Return the neighbors of node n.  Use "G[n]".

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print G[0]
        {1: 1}

        Notes
        -----
        G[n] is similar to G.neighbors(n) but the internal data dictionary
        is returned instead of a list.

        G[u][v] returns the edge data for edge (u,v).

        >>> G=nx.path_graph(4)
        >>> print G[0][1]
        1

        Assigning G[u][v] may corrupt the graph data structure.
        """
        return self.adj[n]
    

    def add_node(self, n):
        """Add a single node n.

        Parameters
        ----------
        n : node
            A node n can be any hashable Python object except None.

            A hashable object is one that can be used as a key in a Python
            dictionary. This includes strings, numbers, tuples of strings
            and numbers, etc. 

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3=nx.complete_graph(3)
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Notes
        -----
        On many platforms hashable items also include mutables such as
        Graphs, though one should be careful that the hash doesn't
        change on mutables.

        """
        if n not in self.adj:
            self.adj[n] = {}


    def add_nodes_from(self, nbunch):
        """Add nodes from nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_nodes_from('Hello')
        >>> K3=nx.complete_graph(3)
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes())
        [0, 1, 2, 'H', 'e', 'l', 'o']

        """
        for n in nbunch:
            if n not in self.adj:
                self.adj[n]={}


    def remove_node(self,n):
        """Remove node n.

        Removes the node n and adjacent edges in the graph.
        Attempting to remove a non-existent node will raise an exception.

        Examples
        --------
        >>> G=nx.complete_graph(3)  # complete graph on 3 nodes, K3
        >>> G.edges()
        [(0, 1), (0, 2), (1, 2)]
        >>> G.remove_node(1)
        >>> G.edges()
        [(0, 2)]

        """
        adj = self.adj
        try:
            nbrs = adj[n].keys() # keys handles self-loops (allow mutation later)
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError("node %s not in graph"%(n,))
        for u in nbrs:  
            del adj[u][n]   # remove all edges n-u in graph
        del adj[n]          # now remove node


    delete_node = remove_node        

    def remove_nodes_from(self, nbunch):
        """Remove nodes specified in nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.

        Examples
        --------
        >>> G=nx.complete_graph(3)  # complete graph on 3 nodes, K3
        >>> e=G.nodes()
        >>> e
        [0, 1, 2]
        >>> G.remove_nodes_from(e)
        >>> G.nodes()
        []

        """
        adj = self.adj
        for n in nbunch:
            try: 
                for u in adj[n].keys():   # keys() handles self-loops 
                    del adj[u][n]         #(allows mutation of dict in loop)
                del adj[n]
            except KeyError:
                pass

    delete_nodes_from = remove_nodes_from

    def nodes_iter(self):
        """Return an iterator for the nodes.

        Examples
        --------
        >>> G=nx.path_graph(3)
        >>> for n in G.nodes_iter():
        ...     print n,
        0 1 2

        You can also say

        >>> G=nx.path_graph(3)
        >>> for n in G:
        ...     print n,
        0 1 2

        Notes
        -----
        It is simpler and equivalent to use the expression "for n in G"

        >>> G=nx.path_graph(3)
        >>> for n in G:
        ...     print n,
        0 1 2

        """
        return self.adj.iterkeys()

    def nodes(self):
        """Return a list of the nodes.

        Examples
        --------
        >>> G=nx.path_graph(3)
        >>> print G.nodes()
        [0, 1, 2]

        """
        return self.adj.keys()

    def number_of_nodes(self):
        """Return the number of nodes.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print len(G)
        4

        Notes
        -----
        This is the same as
             
        >>> len(G)
        4

        and

        >>> G.order()
        4

        """
        return len(self.adj)

    def order(self):
        """Return the number of nodes.

        See Also
        --------
        number_of_nodes, __len__ 

        """
        return len(self.adj)

    def has_node(self,n):
        """Return True if graph has node n.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print G.has_node(0)
        True
        
        Notes
        -----

        It is more readable and simpler to use
        >>> 0 in G
        True
        
        """
        try:
            return n in self.adj
        except TypeError:
            return False

    def add_edge(self, u, v, data=1):  
        """Add an edge between u and v with optional data.

        The nodes u and v will be automatically added if they are 
        not already in the graph.  

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers. 
            Nodes must be hashable (and not None) Python objects.

        data : Python object            
            Edge data (or labels or objects) can be entered via the 
            optional argument data which defaults to 1.

            Some NetworkX algorithms are designed for weighted
            graphs for which the edge data must be a number. These
            may behave unpredictably for edge data that isn't a number.

        Examples
        --------
        The following all add the edge e=(1,2) to graph G.
        
        >>> G=nx.Graph()
        >>> e=(1,2)
        >>> G.add_edge( 1, 2 )          # explicit two node form
        >>> G.add_edge( *e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        Associate the data myedge to the edge (1,2).

        >>> myedge=1.3
        >>> G.add_edge(1, 2, myedge)

        Notes 
        -----
        Adding an edge that already 
        exists *overwrites* the edgedata.

        See Also
        --------
        add_edges_from : add a collection of edges
        MultiGraph.add_edge : the MultiGraph class allows parallel edges 

        """
        # add nodes            
        if u not in self.adj: 
            self.adj[u] = {}
        if v not in self.adj: 
            self.adj[v] = {}
        # add the edge
        self.adj[u][v] = data
        self.adj[v][u] = data


    def add_edges_from(self, ebunch, data=1):  
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : list or container of edges
            The container must be iterable or an iterator.  It is
            iterated over once. Adding the same edge twice has no
            effect and does not raise an exception.  The edges in
            ebunch must be 2-tuples (u,v) or 3-tuples (u,v,d).

         data : any Python object            
             The default data for edges with no data given.
             If unspecified the integer 1 will be used.

        See Also
        --------
        add_edge : add a single edge

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_edges_from([(0,1),(1,2)]) # using a list of edge tuples
        >>> e=zip(range(0,3),range(1,4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3
  
        """
        for e in ebunch:
            ne=len(e)
            if ne==3:
                u,v,d = e
            elif ne==2:
                u,v = e  
                d = data
            else: 
                raise NetworkXError,"Edge tuple %s must be a 2-tuple or 3-tuple."%(e,)
            if u not in self.adj: 
                self.adj[u] = {}
            if v not in self.adj: 
                self.adj[v] = {}
            self.adj[u][v] = d
            self.adj[v][u] = d


    def remove_edge(self, u, v): 
        """Remove the edge between (u,v).

        Parameters
        ----------
        u,v: nodes 
            

        See Also
        --------
        remove_edges_from : remove a collection of edges

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.remove_edge(0,1)
        >>> e=(1,2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple
        >>> e=(2,3,'data')
        >>> G.remove_edge(*e[:2]) # edge tuple with data

        """
        try:
            del self.adj[u][v]   
            if u != v:  # self loop needs only one entry removed
                del self.adj[v][u]   
        except KeyError: 
            raise NetworkXError("edge %s-%s not in graph"%(u,v))


    delete_edge=remove_edge


    def remove_edges_from(self, ebunch): 
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            A container of edge 2-tuples (u,v) or edge 3-tuples(u,v,d) 
            though d is ignored unless we are a multigraph.

        See Also
        --------
        remove_edge : remove a single edge
            
        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> ebunch=[(1,2),(2,3)]
        >>> G.remove_edges_from(ebunch) 

        Notes
        -----
        Will fail silently if the edge (u,v) is not in the graph.

        """
        for e in ebunch:
            u,v = e[:2]  # ignore edge data if present
            if u in self.adj and v in self.adj[u]:
                del self.adj[u][v]   
                if u != v:  # self loop needs only one entry deleted
                    del self.adj[v][u]   


    delete_edges_from = remove_edges_from

    def has_neighbor(self, u, v):
        """Return True if node u has neighbor v.

        This returns True if there exists any edge (u,v,data) for some data.

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers. 
            Nodes must be hashable (and not None) Python objects.


        See Also
        --------
        has_edge : check for an edge with optional data check
        
        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.has_neighbor(0,1)
        True
        >>> G.has_edge(0,1) # same as has_neighbor
        True
        >>> 1 in G[0]  # this gives KeyError if u not in G
        True

        """
        try:
            return v in self.adj[u]
        except KeyError:
            return False

    def has_edge(self, u, v):
        """Return True if the edge (u,v) is in the graph, False otherwise. 

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers. 
            Nodes must be hashable (and not None) Python objects.
            
        See Also
        --------
        has_neighbor()

        Examples
        --------
        Can be called either using two nodes u,v or edge tuple (u,v)

        >>> G=nx.path_graph(4)
        >>> G.has_edge(0,1)  # called using two nodes
        True
        >>> e=(0,1)
        >>> G.has_edge(*e)  #  e is a 2-tuple (u,v)
        True
        >>> e=(0,1,'data')
        >>> G.has_edge(*e[:2])  # e is a 3-tuple (u,v,d)
        True

        The following syntax are all equivalent: 
        
        >>> G.has_neighbor(0,1)
        True
        >>> G.has_edge(0,1)
        True
        >>> 1 in G[0]  # though this gives KeyError if 0 not in G
        True
        
        """
        try:
            return v in self.adj[u]
        except KeyError:
            return False


    def neighbors(self, n):
        """Return a list of the nodes connected to the node n.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.neighbors(0)
        [1]

        Notes
        -----
        It is sometimes more convenient (and faster) to access
        the adjacency dictionary as G[n]

        >>> G=nx.Graph()
        >>> G.add_edge('a','b','data')
        >>> G['a']
        {'b': 'data'}
        """
        try:
            return self.adj[n].keys()
        except KeyError:
            raise NetworkXError("node %s not in graph"%(n,))

    def neighbors_iter(self, n):
        """Return an iterator over all neighbors of node n.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> print [n for n in G.neighbors(0)]
        [1]

        Notes
        -----
        It is faster to iterate over the nodes using the idiom

        >>> print [n for n in G[0]]
        [1]
        
        """
        try:
            return self.adj[n].iterkeys()
        except KeyError:
            raise NetworkXError("node %s not in graph"%(n,))

    def edges(self, nbunch=None, data=False):
        """Return a list of edges.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        data : bool
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True)


        Returns
        --------
        Edges that are adjacent to any node in nbunch,
        or a list of all edges if nbunch is not specified.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.edges()
        [(0, 1), (1, 2), (2, 3)]
        >>> G.edges(data=True) # default edge data is 1
        [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        """
        return list(self.edges_iter(nbunch, data))

    def edges_iter(self, nbunch=None, data=False):
        """Return an iterator over the edges.
        
        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        data : bool
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True)

        Returns
        -------
        An iterator over edges that are adjacent to any node in nbunch,
        or over all edges if nbunch is not specified.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.edges()
        [(0, 1), (1, 2), (2, 3)]
        >>> G.edges(data=True) # default edge data is 1
        [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        """
        seen={}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,data in nbrs.iteritems():
                    if nbr not in seen:
                        yield (n,nbr,data)
                seen[n]=1
        else:
            for n,nbrs in nodes_nbrs:
                for nbr in nbrs:
                    if nbr not in seen:
                        yield (n,nbr)
                seen[n] = 1
        del seen


    def get_edge_data(self, u, v, default=None):
        """Return the data associated with the edge (u,v).

        Parameters
        ----------
        u,v : nodes

        default:  any Python object            
            Value to return if the edge (u,v) is not found.
            The default is the Python None object.

        Examples
        --------
        >>> G=nx.path_graph(4) # path graph with edge data all set to 1
        >>> G.get_edge_data(0,1) 
        1
        >>> e=(0,1)
        >>> G.get_edge_data(*e) # tuple form
        1
        >>> G.get_edge_data('a','b',default=0) # edge not in graph, return 0
        0

        Notes
        -----
        It is faster to use G[u][v].

        >>> G[0][1]
        1

        """
        try:
            return self.adj[u][v]
        except KeyError:
            return default

    def adjacency_list(self):
        """Return an adjacency list as a Python list of lists

        The output adjacency list is in the order of G.nodes().
        For directed graphs, only outgoing adjacencies are included. 

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.adjacency_list() # in sorted node order 0,1,2,3
        [[1], [0, 2], [1, 3], [2]]

        """
        return map(list,self.adj.itervalues())
        
    def adjacency_iter(self):
        """Return an iterator of (node, adjacency dict) tuples for all 
        nodes.

        This is the fastest way to look at every edge. 
        For directed graphs, only outgoing adjacencies are included.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> [(n,nbrdict) for n,nbrdict in G.adjacency_iter()]
        [(0, {1: 1}), (1, {0: 1, 2: 1}), (2, {1: 1, 3: 1}), (3, {2: 1})]

        Notes
        -----
        The dictionary returned is part of the internal graph data structure; 
        changing it could corrupt that structure.
        This is meant for fast inspection, not mutation.

        For MultiGraph/MultiDiGraph multigraphs, a list of edge 
        data is the value in the dict.

        """
        return self.adj.iteritems()



    def degree(self, nbunch=None, with_labels=False, weighted=False):
        """Return the degree of a node or nodes.

        The node degree is the number of edges adjacent to that node. 

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        with_labels : False|True
            Return a list of degrees (False) or a dictionary of
            degrees keyed by node (True).

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.degree(0)
        1
        >>> G.degree([0,1])
        [1, 2]
        >>> G.degree([0,1],with_labels=True)
        {0: 1, 1: 2}

        """
        if with_labels:           # return a dict
            return dict(self.degree_iter(nbunch,weighted=weighted))
        elif nbunch in self:      # return a single node
            return self.degree_iter(nbunch,weighted=weighted).next()[1]
        else:                     # return a list
            return [d for (n,d) in self.degree_iter(nbunch,weighted=weighted)]

    def degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, degree). 

        The node degree is the number of edges adjacent to that node. 

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        weighted : False|True
            If the graph is weighted return the weighted degree
            (the sum of edge weights).

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> list(G.degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.degree_iter([0,1]))
        [(0, 1), (1, 2)]
        """
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                yield (n,sum(nbrs.itervalues())+(n in nbrs and nbrs[n]))
        else:
            for n,nbrs in nodes_nbrs:
                yield (n,len(nbrs)+(n in nbrs)) # return tuple (n,degree)


    def clear(self):
        """Remove all nodes and edges.

        This also removes the name.
        
        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.clear()
        >>> G.nodes()
        []
        >>> G.edges()
        []

        """

        self.name = ''
        self.adj.clear() 

    def copy(self):
        """Return a copy of the graph.

        Notes
        -----
        This makes a complete of the graph but does not make copies
        of any underlying node or edge data.  The node and edge data
        in the copy still point to the same objects as in the original.
        """
        H=self.__class__(self)
        H.name=self.name
        return H

    def to_directed(self):
        """Return a directed representation of the graph.
 
        A new directed graph  is returned with the same name, same nodes, 
        and with each edge (u,v,data) replaced by two directed edges
        (u,v,data) and (v,u,data).
        
        """
        from networkx import DiGraph 
        G=DiGraph()
        G.add_nodes_from(self)
        G.add_edges_from( ((u,v,data) 
                           for u,nbrs in self.adjacency_iter() 
                           for v,data in nbrs.iteritems()) )
        return G

    def to_undirected(self):
        return self.copy()

    def subgraph(self, nbunch, copy=True):
        """Return the subgraph induced on nodes in nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        copy : bool (default True)
            If True return a new graph holding the subgraph.
            Otherwise, the subgraph is created in the original 
            graph by deleting nodes not in nbunch.  
            Warning: this can destroy the graph.

            

        """
        bunch =set(self.nbunch_iter(nbunch))

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
                H_adj[n] = dict( ((u,d) for u,d in self_adj[n].iteritems() 
                                 if u in bunch) )
            return H


    def nodes_with_selfloops(self):
        """Return a list of nodes with self loops.

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> G.nodes_with_selfloops()
        [1]

        """
        return [ n for n,nbrs in self.adj.iteritems() if n in nbrs ]

    def selfloop_edges(self,data=False):
        """Return a list of selfloop edges

        Parameters
        -----------
        data : bool
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True)

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> G.selfloop_edges()
        [(1, 1)]
        >>> G.selfloop_edges(data=True)
        [(1, 1, 1)]

        """
        if data:
            return [ (n,n,nbrs[n]) 
                     for n,nbrs in self.adj.iteritems() if n in nbrs ]
        else:
            return [ (n,n) 
                     for n,nbrs in self.adj.iteritems() if n in nbrs ]


    def number_of_selfloops(self):
        """Return the number of selfloop edges (edge from a node to
        itself).

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> G.number_of_selfloops()
        1

        """
        return len(self.nodes_with_selfloops())

    def size(self, weighted=False):
        """Return the number of edges.

        Parameters
        ----------
        weighted : bool, optional
           If True return the sum of the edge weights.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.size()
        3

        >>> G=nx.Graph()
        >>> G.add_edge('a','b',2)
        >>> G.add_edge('b','c',4)
        >>> G.size()
        2
        >>> G.size(weighted=True)
        6

        See Also
        --------
        number_of_edges

        """

        return sum(self.degree(weighted=weighted))/2

    def number_of_edges(self, u=None, v=None):
        """Return the number of edges between two nodes.

        Parameters
        ----------
        u,v : nodes 
            If u and v are specified, return the number of edges between 
            u and v. Otherwise return the total number of all edges.
            
        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> G.number_of_edges()
        3
        >>> G.number_of_edges(0,1) 
        1
        >>> e=(0,1)
        >>> G.number_of_edges(*e)
        1

        See Also
        --------
        size : number of edges or option for sum of all edge weights

        """
        if u is None: return self.size()
        if v in self.adj[u]:
            return 1
        else:
            return 0


    def add_star(self, nlist, data=None):
        """Add a star.

        The first node in nlist is the middle of the star.  It is connected 
        to all other nodes in nlist.

        Parameters
        ----------
        nlist : list 
            A list of nodes. 
        
        data : list or iterable, optional             
            Data to add to the edges in the path.  
            The length should be one less than len(nlist).

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_star([0,1,2,3])
        >>> G.add_star([10,11,12],data=['a','b'])

        """
        if data is None:
            v=nlist[0]
            edges=((v,n) for n in nlist[1:])
        else:
            # if len(data)<len(nlist) only len(data) items will be added
            v=nlist[0]
            edges=((v,n,d) for n,d in zip(nlist[1:],data))
        self.add_edges_from(edges)

    def add_path(self, nlist, data=None):
        """Add a path.
        
        Parameters
        ----------
        nlist : list 
            A list of nodes.  A path will be constructed from
            the nodes (in order) and added to the graph.
        
        data : list or iterable, optional             
            Data to add to the edges in the path.  
            The length should be one less than len(nlist).

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_path([0,1,2,3])
        >>> G.add_path([10,11,12],data=['a','b'])

        """
        if data is None:
            edges=zip(nlist[:-1],nlist[1:])
        else:
            # if len(data)<len(nlist) only len(data) items will be added
            edges=zip(nlist[:-1],nlist[1:],data)
        self.add_edges_from(edges)

    def add_cycle(self, nlist, data=None):
        """Add a cycle.
        
        Parameters
        ----------
        nlist : list 
            A list of nodes.  A cycle will be constructed from
            the nodes (in order) and added to the graph.
        
        data : list or iterable, optional             
            Data to add to the edges in the path.  
            The length should be the same as nlist.

        Examples
        --------
        >>> G=nx.Graph()
        >>> G.add_cycle([0,1,2,3])
        >>> G.add_cycle([10,11,12],data=['a','b','c'])

        """
        if data is None:
            edges=zip(nlist,nlist[1:]+[nlist[0]])
        else:
            # if len(data)<len(nlist) only len(data) items will be added
            edges=zip(nlist,nlist[1:]+[nlist[0]],data)
        self.add_edges_from(edges)


    def nbunch_iter(self, nbunch=None):
        """Return an iterator of nodes contained
        in nbunch that are also in the graph.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once
            (thus it should be an iterator or be iterable).  Each
            element of the container should be a valid node type: any
            hashable type except None.
            If nbunch is None, return all edges data in the graph.
            Nodes in nbunch that are not in the graph will be (quietly) ignored.

        Notes 
        -----
        When nbunch is an iterator, the returned iterator yields values 
        directly from nbunch, becoming exhausted when nbunch is exhausted.
        
        To test whether nbunch is a single node, one can use 
        "if nbunch in self:", even after processing with this routine.
        
        If nbunch is not a node or a (possibly empty) sequence/iterator
        or None, a NetworkXError is raised.  Also, if any values returned
        by an iterator nbunch is not hashable, a NetworkXError is raised.
        """
        if nbunch is None:   # include all nodes via iterator
            bunch=self.adj.iterkeys()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch].__iter__()
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist,adj):
                try:    
                    for n in nlist:
                        if n in adj:
                            yield n
                except TypeError,e:
                    message=e.args[0]
                    print message
                    # capture error for non-sequence/iterator nbunch.
                    if 'iterable' in message:  
                        raise NetworkXError(
                            "nbunch is not a node or a sequence of nodes.")
                    # capture error for unhashable node.
                    elif 'hashable' in message: 
                        raise NetworkXError(
                            "Node %s in the sequence nbunch is not a valid node."%n)
                    else: raise
            bunch=bunch_iter(nbunch,self.adj)
        return bunch
