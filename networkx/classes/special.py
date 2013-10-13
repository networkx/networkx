"""Special classes to allow for dict-like storage within graph classes.

The Graph class uses a dict-of-dict-of-dict data structure.
The outer dict holds adjacency lists keyed by node.
The next dict represents the adjacency list and  holds 
edge data keyed by neighbor.  The inner dict represents the
edge data and holds edge attribute values keyed by attribute names.

This class allows easy replacement of each dict class in this
structure.  Users who want special behavior can subclass the dict
class or use existin special subclasses from the standard library 
such as collections.OrderedDict.  The NetworkX code needs these
objects to be dict-like as documented below but otherwise the
objects can add functionality without affecting networkx.  As
always with NetworkX, the data structure is somewhat exposed by
our API so updating and changing the data directly can render
the data structure corrupt.  It is best to add/remove edges and
nodes through the NetworkX API.

The main undirected graph class provided here is SpecialGraph.
Similarly we provide SpecialDiGraph.  We haven't implemented
Multiedge versions yet, but it would be a straight-forward 
extension to dict-of-dict-of-dict-of-dict.
"""
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from copy import deepcopy
import networkx as nx
from networkx.classes.graph import Graph
from networkx.classes.digraph import DiGraph
from networkx.exception import NetworkXError
import networkx.convert as convert

__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'])

class SpecialGraph(Graph):
    """
    Special data structure for undirected graphs.

    This subclass of the Graph class allows replacement of the
    dict data-structure with dict-like objects.
    
    There are three types of dicts used in the dict-of-dict-of-dict
    structure and each can be replaced by a user defined dict-like
    object.  In general, the dict-like features should be maintained
    but extra features can be added.

    The Graph class uses a dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency lists keyed by node.
    The next dict (adj_list) represents the adjacency list and holds 
    edge data keyed by neighbor.  The inner dict (edge_info) represents 
    the edge data and holds edge attribute values keyed by attribute names.

    Each can be replaced by providing a factory function upon graph
    creation.  The factory function should return a dict-like object
    and will be used each time one of the data-structure dicts are created.

    Parameters
    ----------
    data : input graph
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.  If the corresponding optional Python
        packages are installed the data can also be a NumPy matrix
        or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.

    node_dict_factory : function, optional (default: dict)
        Factory function to be used to create the outer-most dict
        in the data structure that holds adjacency lists keyed by node.
        It should require no arguments and return a dict-like object. 

    adjlist_dict_factory : function, optional (default: dict)    
        Factory function to be used to create the adjacency list
        dict which holds edge data keyed by neighbor.
        It should require no arguments and return a dict-like object. 

    edge_attr_dict_factory : function, optional (default: dict)    
        Factory function to be used to create the edge attribute
        dict which holds attrbute values keyed by attribute name.
        It should require no arguments and return a dict-like object. 

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    Graph
    DiGraph
    SpecialDiGraph

    Examples
    --------
    Create a standard NetworkX graph object.

    >>> G = nx.SpecialGraph()

    Create a graph object that tracks the order nodes are added.

    >>> from collections import OrderedDict
    >>> G = nx.SpecialGraph(node_dict_factory=OrderedDict)
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1), (1,1)) )
    >>> G.edges()
    [(2, 1), (2, 2), (1, 1)]

    Create a graph object that tracks the order nodes are added
    and for each node track the order that neighbors are added.

    >>> G = nx.SpecialGraph(node_dict_factory=OrderedDict,
    ...          adjlist_dict_factory=OrderedDict)
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1), (1,1)) )
    >>> G.edges()
    [(2, 2), (2, 1), (1, 1)]
    
    Create a low memory graph class that effectively disallows edge
    attributes by using a single attribute dict for all edges.
    This reduces the memory used, but you lose edge attributes.

    >>> all_edge_dict = {'weight': 1}
    >>> G = nx.SpecialGraph(edge_attr_dict_factory=lambda :all_edge_dict)
    >>> G.add_edge(2,1)
    >>> G.edges(data= True)
    [(1, 2, {'weight': 1})]
    >>> G.add_edge(2,2)
    >>> G[2][1] is G[2][2]
    True
    """
    def __init__(self, data=None,
            node_dict_factory=dict,
            adjlist_dict_factory=dict,
            edge_attr_dict_factory=dict,
            **attr):
        self.graph = {}   # dictionary for graph attributes
        self.node = node_dict_factory()  # empty node dict
        self.adj = node_dict_factory()   # empty adjacency dict
        self.node_dict_factory=node_dict_factory
        self.adjlist_dict_factory=adjlist_dict_factory
        self.edge_attr_dict_factory=edge_attr_dict_factory
        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data,create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)
        self.edge = self.adj

    def add_node(self, n, attr_dict=None, **attr):
        """Add a single node n and update node attributes.

        Parameters
        ----------
        n : node
            A node can be any hashable Python object except None.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of node attributes.  Key/value pairs will
            update existing data associated with the node.
        attr : keyword arguments, optional
            Set or change attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Use keywords set/change node attributes:

        >>> G.add_node(1,size=10)
        >>> G.add_node(3,weight=0.4,UTM=('13S',382871,3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        if n not in self.node:
            self.adj[n] = self.adjlist_dict_factory()
            self.node[n] = attr_dict
        else: # update attr even if node already exists
            self.node[n].update(attr_dict)


    def add_nodes_from(self, nodes, **attr):
        """Add multiple nodes.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes (list, dict, set, etc.).
            OR
            A container of (node, attribute dict) tuples.
            Node attributes are updated using the attribute dict.
        attr : keyword arguments, optional (default= no attributes)
            Update attributes for all nodes in nodes.
            Node attributes specified in nodes as a tuple
            take precedence over attributes specified generally.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_nodes_from('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes(),key=str)
        [0, 1, 2, 'H', 'e', 'l', 'o']

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1,2], size=10)
        >>> G.add_nodes_from([3,4], weight=0.4)

        Use (node, attrdict) tuples to update attributes for specific
        nodes.

        >>> G.add_nodes_from([(1,dict(size=11)), (2,{'color':'blue'})])
        >>> G.node[1]['size']
        11
        >>> H = nx.Graph()
        >>> H.add_nodes_from(G.nodes(data=True))
        >>> H.node[1]['size']
        11

        """
        for n in nodes:
            try:
                newnode=n not in self.node
            except TypeError:
                nn,ndict = n
                if nn not in self.node:
                    self.adj[nn] = self.adjlist_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)
                continue
            if newnode:
                self.adj[n] = self.adjlist_dict_factory()
                self.node[n] = attr.copy()
            else:
                self.node[n].update(attr)

    def add_edge(self, u, v, attr_dict=None, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by providing
        a dictionary with key/value pairs.  See examples below.

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with the edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        Adding an edge that already exists updates the edge data.

        Many NetworkX algorithms designed for weighted graphs use as
        the edge weight a numerical value assigned to a keyword
        which by default is 'weight'.

        Examples
        --------
        The following all add the edge e=(1,2) to graph G:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1,2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # set up attribute dictionary
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.node:
            self.adj[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.node:
            self.adj[v] = self.adjlist_dict_factory()
            self.node[v] = {}
        # add the edge
        datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
        datadict.update(attr_dict)
        self.adj[u][v] = datadict
        self.adj[v][u] = datadict


    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as as 2-tuples (u,v) or
            3-tuples (u,v,d) where d is a dictionary containing edge
            data.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with each edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.


        See Also
        --------
        add_edge : add a single edge
        add_weighted_edges_from : convenient way to add weighted edges

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0,1),(1,2)]) # using a list of edge tuples
        >>> e = zip(range(0,3),range(1,4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1,2),(2,3)], weight=3)
        >>> G.add_edges_from([(3,4),(1,4)], label='WN2898')
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            ne=len(e)
            if ne==3:
                u,v,dd = e
            elif ne==2:
                u,v = e
                dd = {}
            else:
                raise NetworkXError(\
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            if u not in self.node:
                self.adj[u] = self.adjlist_dict_factory()
                self.node[u] = {}
            if v not in self.node:
                self.adj[v] = self.adjlist_dict_factory()
                self.node[v] = {}
            datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
            datadict.update(attr_dict)
            datadict.update(dd)
            self.adj[u][v] = datadict
            self.adj[v][u] = datadict


    def to_directed(self):
        """Return a directed representation of the graph.

        Returns
        -------
        G : DiGraph
            A directed graph with the same name, same nodes, and with
            each edge (u,v,data) replaced by two directed edges
            (u,v,data) and (v,u,data).

        Notes
        -----
        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar D=DiGraph(G) which returns a
        shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, http://docs.python.org/library/copy.html.

        Examples
        --------
        >>> G = nx.Graph()   # or MultiGraph, etc
        >>> G.add_path([0,1])
        >>> H = G.to_directed()
        >>> H.edges()
        [(0, 1), (1, 0)]

        If already directed, return a (deep) copy

        >>> G = nx.DiGraph()   # or MultiDiGraph, etc
        >>> G.add_path([0,1])
        >>> H = G.to_directed()
        >>> H.edges()
        [(0, 1)]
        """
        G=SpecialDiGraph(node_dict_factory=self.node_dict_factory,
                adjlist_dict_factory=self.adjlist_dict_factory,
                edge_attr_dict_factory=self.edge_attr_dict_factory)
        G.name=self.name
        G.add_nodes_from(self)
        G.add_edges_from( ((u,v,deepcopy(data))
                           for u,nbrs in self.adjacency_iter()
                           for v,data in nbrs.items()) )
        G.graph=deepcopy(self.graph)
        G.node=deepcopy(self.node)
        return G

    def subgraph(self, nbunch):
        """Return the subgraph induced on nodes in nbunch.

        The induced subgraph of the graph contains the nodes in nbunch
        and the edges between those nodes.

        Parameters
        ----------
        nbunch : list, iterable
            A container of nodes which will be iterated through once.

        Returns
        -------
        G : Graph
            A subgraph of the graph with the same edge attributes.

        Notes
        -----
        The graph, edge or node attributes just point to the original graph.
        So changes to the node or edge structure will not be reflected in
        the original graph while changes to the attributes will.

        To create a subgraph with its own copy of the edge/node attributes use:
        nx.Graph(G.subgraph(nbunch))

        If edge attributes are containers, a deep copy can be obtained using:
        G.subgraph(nbunch).copy()

        For an inplace reduction of a graph to a subgraph you can remove nodes:
        G.remove_nodes_from([ n in G if n not in set(nbunch)])

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2,3])
        >>> H = G.subgraph([0,1,2])
        >>> H.edges()
        [(0, 1), (1, 2)]
        """
        bunch =self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__(node_dict_factory=self.node_dict_factory,
                adjlist_dict_factory=self.adjlist_dict_factory,
                edge_attr_dict_factory=self.edge_attr_dict_factory)
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n]=self.node[n]
        # namespace shortcuts for speed
        H_adj=H.adj
        self_adj=self.adj
        # add nodes and edges (undirected method)
        for n in H.node:
            Hnbrs=H.adjlist_dict_factory()
            H_adj[n]=Hnbrs
            for nbr,d in self_adj[n].items():
                if nbr in H_adj:
                    # add both representations of edge: n-nbr and nbr-n
                    Hnbrs[nbr]=d
                    H_adj[nbr][n]=d
        H.graph=self.graph
        return H


class SpecialDiGraph(DiGraph):
    """
    Special class for directed graphs.

    This subclass of the DiGraph class allows replacement of the
    dict data-structure with dict-like objects.
    
    There are three types of dicts used in the dict-of-dict-of-dict
    structure and each can be replaced by a user defined dict-like
    object.  In general, the dict-like features should be maintained
    but extra features can be added.

    Each can be replaced by providing a factory function upon graph
    creation.  The factory function should return a dict-like object
    and will be used each time one of the data-structure dicts are created.

    Parameters
    ----------
    data : input graph
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.  If the corresponding optional Python
        packages are installed the data can also be a NumPy matrix
        or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.

    node_dict_factory : function, optional (default: dict)
        Factory function to be used to create the outer-most dict
        in the data structure that holds adjacency lists keyed by node.
        It should require no arguments and return a dict-like object. 

    adjlist_dict_factory : function, optional (default: dict)    
        Factory function to be used to create the adjacency list
        dict which holds edge data keyed by neighbor.
        It should require no arguments and return a dict-like object. 

    edge_attr_dict_factory : function, optional (default: dict)    
        Factory function to be used to create the edge attribute
        dict which holds attrbute values keyed by attribute name.
        It should require no arguments and return a dict-like object. 

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    DiGraph
    SpecialGraph

    Examples
    --------
    Create a standard NetworkX digraph object. 

    >>> G = nx.SpecialDiGraph()

    Create a digraph object that tracks the order nodes are added.

    >>> from collections import OrderedDict
    >>> G = nx.SpecialDiGraph(node_dict_factory=OrderedDict)
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1), (1,1)) )
    >>> G.edges()
    [(2, 1), (2, 2), (1, 1)]

    Create a digraph object that tracks the order nodes are added
    and for each node track the order that neighbors are added.

    >>> G = nx.SpecialDiGraph(node_dict_factory=OrderedDict,
    ...          adjlist_dict_factory=OrderedDict)
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1), (1,1)) )
    >>> G.edges()
    [(2, 2), (2, 1), (1, 1)]
    
    Create a low memory digraph class that is unable to hold edge data.
    Warning: this class will not work with any NetworkX functions
    that expect edge attribute data.

    >>> all_edge_dict = {'weight': 1}
    >>> G = nx.SpecialDiGraph(edge_attr_dict_factory=lambda :all_edge_dict)
    >>> G.add_edge(2,1)
    >>> G.edges(data= True)
    [(2, 1, {'weight': 1})]
    >>> G.add_edge(2,2)
    >>> G[2][1] is G[2][2]
    True
    """
    def __init__(self, data=None,
            node_dict_factory=dict,
            adjlist_dict_factory=dict,
            edge_attr_dict_factory=dict,
            **attr):
        self.graph = {} # dictionary for graph attributes
        self.node = node_dict_factory() # dictionary for node attributes
        # We store two adjacency lists:
        # the  predecessors of node n are stored in the dict self.pred
        # the successors of node n are stored in the dict self.succ=self.adj
        self.adj = node_dict_factory()  # empty adjacency dictionary
        self.pred = node_dict_factory()  # predecessor
        self.succ = self.adj  # successor

        self.node_dict_factory=node_dict_factory
        self.adjlist_dict_factory=adjlist_dict_factory
        self.edge_attr_dict_factory=edge_attr_dict_factory

        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data,create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)
        self.edge=self.adj


    def add_node(self, n, attr_dict=None, **attr):
        """Add a single node n and update node attributes.

        Parameters
        ----------
        n : node
            A node can be any hashable Python object except None.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of node attributes.  Key/value pairs will
            update existing data associated with the node.
        attr : keyword arguments, optional
            Set or change attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Use keywords set/change node attributes:

        >>> G.add_node(1,size=10)
        >>> G.add_node(3,weight=0.4,UTM=('13S',382871,3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        if n not in self.succ:
            self.succ[n] = self.adjlist_dict_factory()
            self.pred[n] = self.adjlist_dict_factory()
            self.node[n] = attr_dict
        else: # update attr even if node already exists
            self.node[n].update(attr_dict)


    def add_nodes_from(self, nodes, **attr):
        """Add multiple nodes.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes (list, dict, set, etc.).
            OR
            A container of (node, attribute dict) tuples.
            Node attributes are updated using the attribute dict.
        attr : keyword arguments, optional (default= no attributes)
            Update attributes for all nodes in nodes.
            Node attributes specified in nodes as a tuple
            take precedence over attributes specified generally.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_nodes_from('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes(),key=str)
        [0, 1, 2, 'H', 'e', 'l', 'o']

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1,2], size=10)
        >>> G.add_nodes_from([3,4], weight=0.4)

        Use (node, attrdict) tuples to update attributes for specific
        nodes.

        >>> G.add_nodes_from([(1,dict(size=11)), (2,{'color':'blue'})])
        >>> G.node[1]['size']
        11
        >>> H = nx.Graph()
        >>> H.add_nodes_from(G.nodes(data=True))
        >>> H.node[1]['size']
        11

        """
        for n in nodes:
            try:
                newnode=n not in self.succ
            except TypeError:
                nn,ndict = n
                if nn not in self.succ:
                    self.succ[nn] = self.adjlist_dict_factory()
                    self.pred[nn] = self.adjlist_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)
                continue
            if newnode:
                self.succ[n] = self.adjlist_dict_factory()
                self.pred[n] = self.adjlist_dict_factory()
                self.node[n] = attr.copy()
            else:
                self.node[n].update(attr)

    def add_edge(self, u, v, attr_dict=None, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by providing
        a dictionary with key/value pairs.  See examples below.

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with the edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        Adding an edge that already exists updates the edge data.

        Many NetworkX algorithms designed for weighted graphs use as
        the edge weight a numerical value assigned to a keyword
        which by default is 'weight'.

        Examples
        --------
        The following all add the edge e=(1,2) to graph G:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1,2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.succ:
            self.succ[u]= self.adjlist_dict_factory()
            self.pred[u]= self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.succ:
            self.succ[v]= self.adjlist_dict_factory()
            self.pred[v]= self.adjlist_dict_factory()
            self.node[v] = {}
        # add the edge
        datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
        datadict.update(attr_dict)
        self.succ[u][v]=datadict
        self.pred[v][u]=datadict

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as as 2-tuples (u,v) or
            3-tuples (u,v,d) where d is a dictionary containing edge
            data.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with each edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.


        See Also
        --------
        add_edge : add a single edge
        add_weighted_edges_from : convenient way to add weighted edges

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0,1),(1,2)]) # using a list of edge tuples
        >>> e = zip(range(0,3),range(1,4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1,2),(2,3)], weight=3)
        >>> G.add_edges_from([(3,4),(1,4)], label='WN2898')
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dict.")
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne==3:
                u,v,dd = e
                assert hasattr(dd,"update")
            elif ne==2:
                u,v = e
                dd = {}
            else:
                raise NetworkXError(\
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            if u not in self.succ:
                self.succ[u] = self.adjlist_dict_factory()
                self.pred[u] = self.adjlist_dict_factory()
                self.node[u] = {}
            if v not in self.succ:
                self.succ[v] = self.adjlist_dict_factory()
                self.pred[v] = self.adjlist_dict_factory()
                self.node[v] = {}
            datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
            datadict.update(attr_dict)
            datadict.update(dd)
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict


    def to_undirected(self, reciprocal=False):
        """Return an undirected representation of the digraph.

        Parameters
        ----------
        reciprocal : bool (optional)
          If True only keep edges that appear in both directions 
          in the original digraph. 

        Returns
        -------
        G : Graph
            An undirected graph with the same name and nodes and
            with edge (u,v,data) if either (u,v,data) or (v,u,data)
            is in the digraph.  If both edges exist in digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

        Notes
        -----
        If edges in both directions (u,v) and (v,u) exist in the
        graph, attributes for the new undirected edge will be a combination of
        the attributes of the directed edges.  The edge data is updated
        in the (arbitrary) order that the edges are encountered.  For
        more customized control of the edge attributes use add_edge().

        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar G=DiGraph(D) which returns a
        shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, http://docs.python.org/library/copy.html.
        """
        H=SpecialGraph(node_dict_factory=self.node_dict_factory,
                adjlist_dict_factory=self.adjlist_dict_factory,
                edge_attr_dict_factory=self.edge_attr_dict_factory)
        H.name=self.name
        H.add_nodes_from(self)
        if reciprocal is True:
            H.add_edges_from( (u,v,deepcopy(d))
                              for u,nbrs in self.adjacency_iter()
                              for v,d in nbrs.items() 
                              if v in self.pred[u])
        else:
            H.add_edges_from( (u,v,deepcopy(d))
                              for u,nbrs in self.adjacency_iter()
                              for v,d in nbrs.items() )
        H.graph=deepcopy(self.graph)
        H.node=deepcopy(self.node)
        return H

    def subgraph(self, nbunch):
        """Return the subgraph induced on nodes in nbunch.

        The induced subgraph of the graph contains the nodes in nbunch
        and the edges between those nodes.

        Parameters
        ----------
        nbunch : list, iterable
            A container of nodes which will be iterated through once.

        Returns
        -------
        G : Graph
            A subgraph of the graph with the same edge attributes.

        Notes
        -----
        The graph, edge or node attributes just point to the original graph.
        So changes to the node or edge structure will not be reflected in
        the original graph while changes to the attributes will.

        To create a subgraph with its own copy of the edge/node attributes use:
        nx.Graph(G.subgraph(nbunch))

        If edge attributes are containers, a deep copy can be obtained using:
        G.subgraph(nbunch).copy()

        For an inplace reduction of a graph to a subgraph you can remove nodes:
        G.remove_nodes_from([ n in G if n not in set(nbunch)])

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2,3])
        >>> H = G.subgraph([0,1,2])
        >>> H.edges()
        [(0, 1), (1, 2)]
        """
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__(node_dict_factory=self.node_dict_factory,
                adjlist_dict_factory=self.adjlist_dict_factory,
                edge_attr_dict_factory=self.edge_attr_dict_factory)
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n]=self.node[n]
        # namespace shortcuts for speed
        H_succ=H.succ
        H_pred=H.pred
        self_succ=self.succ
        # add nodes
        for n in H:
            H_succ[n]=H.adjlist_dict_factory()
            H_pred[n]=H.adjlist_dict_factory()
        # add edges
        for u in H_succ:
            Hnbrs=H_succ[u]
            for v,datadict in self_succ[u].items():
                if v in H_succ:
                    # add both representations of edge: u-v and v-u
                    Hnbrs[v]=datadict
                    H_pred[v][u]=datadict
        H.graph=self.graph
        return H
