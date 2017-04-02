"""Base class for undirected graphs.

The Graph class allows any hashable object as a node
and can associate key/value attribute pairs with each undirected edge.

Self-loops are allowed but multiple edges are not (see MultiGraph).

For directed graphs see DiGraph and MultiDiGraph.
"""
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from __future__ import division
from copy import deepcopy
import networkx as nx
from networkx.exception import NetworkXError
import networkx.convert as convert
from networkx.utils import pairwise

__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'])


class Graph(object):
    """
    Base class for undirected graphs.

    A Graph stores nodes and edges with optional data, or attributes.

    Graphs hold undirected edges.  Self loops are allowed but multiple
    (parallel) edges are not.

    Nodes can be arbitrary (hashable) Python objects with optional
    key/value attributes.

    Edges are represented as links between nodes with optional
    key/value attributes.

    Parameters
    ----------
    data : input graph
        Data to initialize graph. If data=None (default) an empty
        graph is created.  The data can be any format that is supported
        by the to_networkx_graph() function, currently including edge list,
        dict of dicts, dict of lists, NetworkX graph, NumPy matrix
        or 2d ndarray, SciPy sparse matrix, or PyGraphviz graph.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    DiGraph
    MultiGraph
    MultiDiGraph

    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and
    no edges.

    >>> G = nx.Graph()

    G can be grown in several ways.

    **Nodes:**

    Add one node at a time:

    >>> G.add_node(1)

    Add the nodes from any container (a list, dict, set or
    even the lines from a file or the nodes from another graph).

    >>> G.add_nodes_from([2,3])
    >>> G.add_nodes_from(range(100,110))
    >>> H = nx.path_graph(10)
    >>> G.add_nodes_from(H)

    In addition to strings and integers any hashable Python object
    (except None) can represent a node, e.g. a customized node object,
    or even another Graph.

    >>> G.add_node(H)

    **Edges:**

    G can also be grown by adding edges.

    Add one edge,

    >>> G.add_edge(1, 2)

    a list of edges,

    >>> G.add_edges_from([(1,2),(1,3)])

    or a collection of edges,

    >>> G.add_edges_from(H.edges())

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically.  There are no errors when adding
    nodes or edges that already exist.

    **Attributes:**

    Each graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute
    dictionaries named graph, node and edge respectively.

    >>> G = nx.Graph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from() or G.node

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')
    >>> G.node[1]
    {'time': '5pm'}
    >>> G.node[1]['room'] = 714
    >>> del G.node[1]['room'] # remove attribute
    >>> list(G.nodes(data=True))
    [(1, {'time': '5pm'}), (3, {'time': '2pm'})]

    Warning: adding a node to G.node does not add it to the graph.

    Add edge attributes using add_edge(), add_edges_from(), subscript
    notation, or G.edge.

    >>> G.add_edge(1, 2, weight=4.7 )
    >>> G.add_edges_from([(3,4),(4,5)], color='red')
    >>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
    >>> G[1][2]['weight'] = 4.7
    >>> G.edge[1][2]['weight'] = 4

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> len(G)  # number of nodes in graph
    5

    The fastest way to traverse all edges of a graph is via
    adjacency():

    >>> for n, nbrsdict in G.adjacency():
    ...     for nbr, eattr in nbrsdict.items():
    ...        if 'weight' in eattr:
    ...            # Do something useful with the edges
    ...            pass

    But the edges() method is often more convenient:

    >>> for u, v, weight in G.edges(data='weight'):
    ...     if weight is not None:
    ...         # Do something useful with the edges
    ...         pass

    **Reporting:**

    Simple graph information is obtained using methods.
    Reporting methods usually return iterators instead of containers
    to reduce memory usage.
    Methods exist for reporting nodes(), edges(), neighbors() and degree()
    as well as the number of nodes and edges.

    For details on these and other miscellaneous methods, see below.

    **Subclasses (Advanced):**

    The Graph class uses a dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency information keyed by node.
    The next dict (adjlist_dict) represents the adjacency information and holds
    edge data keyed by neighbor.  The inner dict (edge_attr_dict) represents
    the edge data and holds edge attribute values keyed by attribute names.

    Each of these three dicts can be replaced in a subclass by a user defined
    dict-like object. In general, the dict-like features should be
    maintained but extra features can be added. To replace one of the
    dicts create a new graph class by changing the class(!) variable
    holding the factory for that dict-like structure. The variable names
    are node_dict_factory, adjlist_inner_dict_factory, adjlist_outer_dict_factory,
    and edge_attr_dict_factory.

    node_dict_factory : function, (default: dict)
        Factory function to be used to create the dict containing node
        attributes, keyed by node id.
        It should require no arguments and return a dict-like object

    adjlist_outer_dict_factory : function, (default: dict)
        Factory function to be used to create the outer-most dict
        in the data structure that holds adjacency info keyed by node.
        It should require no arguments and return a dict-like object.

    adjlist_inner_dict_factory : function, (default: dict)
        Factory function to be used to create the adjacency list
        dict which holds edge data keyed by neighbor.
        It should require no arguments and return a dict-like object

    edge_attr_dict_factory : function, (default: dict)
        Factory function to be used to create the edge attribute
        dict which holds attrbute values keyed by attribute name.
        It should require no arguments and return a dict-like object.

    Examples
    --------
    Create a graph subclass that tracks the order nodes are added.

    >>> from collections import OrderedDict
    >>> class OrderedNodeGraph(nx.Graph):
    ...     node_dict_factory=OrderedDict
    ...     adjlist_outer_dict_factory=OrderedDict
    >>> G=OrderedNodeGraph()
    >>> G.add_nodes_from((2, 1))
    >>> list(G.nodes())
    [2, 1]
    >>> G.add_edges_from(((2, 2), (2, 1), (1, 1)))
    >>> # Edge addition order is not preserved

    Create a graph object that tracks the order nodes are added
    and for each node track the order that neighbors are added.

    >>> class OrderedGraph(nx.Graph):
    ...    node_dict_factory = OrderedDict
    ...    adjlist_outer_dict_factory = OrderedDict
    ...    adjlist_inner_dict_factory = OrderedDict
    >>> G = OrderedGraph()
    >>> G.add_nodes_from((2, 1))
    >>> list(G.nodes())
    [2, 1]
    >>> G.add_edges_from(((2, 2), (2, 1), (1, 1)))
    >>> list(G.edges())
    [(2, 2), (2, 1), (1, 1)]

    Create a low memory graph class that effectively disallows edge
    attributes by using a single attribute dict for all edges.
    This reduces the memory used, but you lose edge attributes.

    >>> class ThinGraph(nx.Graph):
    ...     all_edge_dict = {'weight': 1}
    ...     def single_edge_dict(self):
    ...         return self.all_edge_dict
    ...     edge_attr_dict_factory = single_edge_dict
    >>> G = ThinGraph()
    >>> G.add_edge(2, 1)
    >>> G[2][1]
    {'weight': 1}
    >>> G.add_edge(2, 2)
    >>> G[2][1] is G[2][2]
    True

    """
    node_dict_factory = dict
    adjlist_outer_dict_factory = dict
    adjlist_inner_dict_factory = dict
    edge_attr_dict_factory = dict

    def __init__(self, data=None, **attr):
        """Initialize a graph with edges, name, graph attributes.

        Parameters
        ----------
        data : input graph
            Data to initialize graph.  If data=None (default) an empty
            graph is created.  The data can be an edge list, or any
            NetworkX graph object.  If the corresponding optional Python
            packages are installed the data can also be a NumPy matrix
            or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.
        name : string, optional (default='')
            An optional name for the graph.
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        See Also
        --------
        convert

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G = nx.Graph(name='my graph')
        >>> e = [(1,2),(2,3),(3,4)]  # list of edges
        >>> G = nx.Graph(e)

        Arbitrary graph attribute pairs (key=value) may be assigned

        >>> G=nx.Graph(e, day="Friday")
        >>> G.graph
        {'day': 'Friday'}

        """
        self.node_dict_factory = ndf = self.node_dict_factory
        self.adjlist_outer_dict_factory = self.adjlist_outer_dict_factory
        self.adjlist_inner_dict_factory = self.adjlist_inner_dict_factory
        self.edge_attr_dict_factory = self.edge_attr_dict_factory

        self.graph = {}   # dictionary for graph attributes
        self.node = ndf()  # empty node attribute dict
        self.adj = self.adjlist_outer_dict_factory()  # empty adjacency dict
        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data, create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)
        self.edge = self.adj

    @property
    def name(self):
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        """Return the graph name.

        Returns
        -------
        name : string
            The name of the graph.

        Examples
        --------
        >>> G = nx.Graph(name='foo')
        >>> str(G)
        'foo'
        """
        return self.name

    def __iter__(self):
        """Iterate over the nodes. Use the expression 'for n in G'.

        Returns
        -------
        niter : iterator
            An iterator over all nodes in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> [n for n in G]
        [0, 1, 2, 3]
        """
        return iter(self.node)

    def __contains__(self, n):
        """Return True if n is a node, False otherwise. Use the expression
        'n in G'.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> 1 in G
        True
        """
        try:
            return n in self.node
        except TypeError:
            return False

    def __len__(self):
        """Return the number of nodes. Use the expression 'len(G)'.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        4

        """
        return len(self.node)

    def __getitem__(self, n):
        """Return a dict of neighbors of node n.  Use the expression 'G[n]'.

        Parameters
        ----------
        n : node
           A node in the graph.

        Returns
        -------
        adj_dict : dictionary
           The adjacency dictionary for nodes connected to n.

        Notes
        -----
        G[n] is similar to G.neighbors(n) but the internal data dictionary
        is returned instead of an iterator.

        Assigning G[n] will corrupt the internal graph data structure.
        Use G[n] for reading data only.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G[0]
        {1: {}}
        """
        return self.adj[n]

    def add_node(self, n, **attr):
        """Add a single node n and update node attributes.

        Parameters
        ----------
        n : node
            A node can be any hashable Python object except None.
        attr : keyword arguments, optional
            Set or change node attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
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
        if n not in self.node:
            self.adj[n] = self.adjlist_inner_dict_factory()
            self.node[n] = attr
        else:  # update attr even if node already exists
            self.node[n].update(attr)

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
            Node attributes specified in nodes as a tuple take 
            precedence over attributes specified via keyword arguments.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
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
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self.node,
            # while pre-2.7.5 ironpython throws on self.adj[n]
            try:
                if n not in self.node:
                    self.adj[n] = self.adjlist_inner_dict_factory()
                    self.node[n] = attr.copy()
                else:
                    self.node[n].update(attr)
            except TypeError:
                nn, ndict = n
                if nn not in self.node:
                    self.adj[nn] = self.adjlist_inner_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)

    def remove_node(self, n):
        """Remove node n.

        Removes the node n and all adjacent edges.
        Attempting to remove a non-existent node will raise an exception.

        Parameters
        ----------
        n : node
           A node in the graph

        Raises
        -------
        NetworkXError
           If n is not in the graph.

        See Also
        --------
        remove_nodes_from

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> list(G.edges())
        [(0, 1), (1, 2)]
        >>> G.remove_node(1)
        >>> list(G.edges())
        []

        """
        adj = self.adj
        try:
            nbrs = list(adj[n].keys())  # keys handles self-loops (allow mutation later)
            del self.node[n]
        except KeyError:  # NetworkXError if n not in self
            raise NetworkXError("The node %s is not in the graph." % (n,))
        for u in nbrs:
            del adj[u][n]   # remove all edges n-u in graph
        del adj[n]          # now remove node

    def remove_nodes_from(self, nodes):
        """Remove multiple nodes.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes (list, dict, set, etc.).  If a node
            in the container is not in the graph it is silently
            ignored.

        See Also
        --------
        remove_node

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = list(G.nodes())
        >>> e
        [0, 1, 2]
        >>> G.remove_nodes_from(e)
        >>> list(G.nodes())
        []

        """
        adj = self.adj
        for n in nodes:
            try:
                del self.node[n]
                for u in list(adj[n].keys()):   # keys() handles self-loops
                    del adj[u][n]  # (allows mutation of dict in loop)
                del adj[n]
            except KeyError:
                pass

    def nodes(self, data=False, default=None):
        """Returns an iterator over the nodes.

        Parameters
        ----------
        data : string or bool, optional (default=False)
            The node attribute returned in 2-tuple (n,ddict[data]).
            If True, return entire node attribute dict as (n,ddict).
            If False, return just the nodes n.

        default : value, optional (default=None)
            Value used for nodes that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        iterator
            An iterator over nodes, or (n,d) tuples of node with data.
            If data is False, an iterator over nodes.
            Otherwise an iterator of 2-tuples (node, attribute value)
            where the attribute is specified in data.
            If data is True then the attribute becomes the
            entire data dictionary.

        Notes
        -----
        If the node data is not required, it is simpler and equivalent
        to use the expression ``for n in G``, or ``list(G)``.

        Examples
        --------
        There are two simple ways of getting a list of all nodes in the graph:

        >>> G = nx.path_graph(3)
        >>> list(G.nodes())
        [0, 1, 2]
        >>> list(G)
        [0, 1, 2]

        To get the node data along with the nodes:

        >>> G.add_node(1, time='5pm')
        >>> G.node[0]['foo'] = 'bar'
        >>> list(G.nodes(data=True))
        [(0, {'foo': 'bar'}), (1, {'time': '5pm'}), (2, {})]
        >>> list(G.nodes(data='foo'))
        [(0, 'bar'), (1, None), (2, None)]
        >>> list(G.nodes(data='time'))
        [(0, None), (1, '5pm'), (2, None)]
        >>> list(G.nodes(data='time', default='Not Available'))
        [(0, 'Not Available'), (1, '5pm'), (2, 'Not Available')]

        If some of your nodes have an attribute and the rest are assumed
        to have a default attribute value you can create a dictionary
        from node/attribute pairs using the `default` keyword argument
        to guarantee the value is never None::

            >>> G = nx.Graph()
            >>> G.add_node(0)
            >>> G.add_node(1, weight=2)
            >>> G.add_node(2, weight=3)
            >>> dict(G.nodes(data='weight', default=1))
            {0: 1, 1: 2, 2: 3}

        """
        if data is True:
            for n, ddict in self.node.items():
                yield (n, ddict)
        elif data is not False:
            for n, ddict in self.node.items():
                d = ddict[data] if data in ddict else default
                yield (n, d)
        else:
            for n in self.node:
                yield n

    def number_of_nodes(self):
        """Return the number of nodes in the graph.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        order, __len__  which are identical

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        3
        """
        return len(self.node)

    def order(self):
        """Return the number of nodes in the graph.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        number_of_nodes, __len__  which are identical

        """
        return len(self.node)

    def has_node(self, n):
        """Return True if the graph contains the node n.

        Parameters
        ----------
        n : node

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_node(0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """
        try:
            return n in self.node
        except TypeError:
            return False

    def add_edge(self, u, v, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary. See examples below.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
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
        >>> G.add_edges_from([(1, 2)])  # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)

        For non-string associations, directly access the edge's attribute
        dictionary.

        >>> G.add_edge(1, 2)
        >>> G[1][2].update({0: 5})
        """
        # add nodes
        if u not in self.node:
            self.adj[u] = self.adjlist_inner_dict_factory()
            self.node[u] = {}
        if v not in self.node:
            self.adj[v] = self.adjlist_inner_dict_factory()
            self.node[v] = {}
        # add the edge
        datadict = self.adj[u].get(v, self.edge_attr_dict_factory())
        datadict.update(attr)
        self.adj[u][v] = datadict
        self.adj[v][u] = datadict

    def add_edges_from(self, ebunch, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as as 2-tuples (u,v) or
            3-tuples (u,v,d) where d is a dictionary containing edge data.
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

        Edge attributes specified in an ebunch take precedence over 
        attributes specified via keyword arguments.

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
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
            elif ne == 2:
                u, v = e
                dd = {}  # doesnt need edge_attr_dict_factory
            else:
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,))
            if u not in self.node:
                self.adj[u] = self.adjlist_inner_dict_factory()
                self.node[u] = {}
            if v not in self.node:
                self.adj[v] = self.adjlist_inner_dict_factory()
                self.node[v] = {}
            datadict = self.adj[u].get(v, self.edge_attr_dict_factory())
            datadict.update(attr)
            datadict.update(dd)
            self.adj[u][v] = datadict
            self.adj[v][u] = datadict

    def add_weighted_edges_from(self, ebunch, weight='weight', **attr):
        """Add all the edges in ebunch as weighted edges with specified
        weights.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the list or container will be added
            to the graph. The edges must be given as 3-tuples (u,v,w)
            where w is a number.
        weight : string, optional (default= 'weight')
            The attribute name for the edge weights to be added.
        attr : keyword arguments, optional (default= no attributes)
            Edge attributes to add/update for all edges.

        See Also
        --------
        add_edge : add a single edge
        add_edges_from : add multiple edges

        Notes
        -----
        Adding the same edge twice for Graph/DiGraph simply updates
        the edge data.  For MultiGraph/MultiDiGraph, duplicate edges
        are stored.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_weighted_edges_from([(0,1,3.0),(1,2,7.5)])
        """
        self.add_edges_from(((u, v, {weight: d}) for u, v, d in ebunch),
                            **attr)

    def remove_edge(self, u, v):
        """Remove the edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove the edge between nodes u and v.

        Raises
        ------
        NetworkXError
            If there is not an edge between u and v.

        See Also
        --------
        remove_edges_from : remove a collection of edges

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, etc
        >>> G.remove_edge(0,1)
        >>> e = (1,2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple
        >>> e = (2,3,{'weight':7}) # an edge with attribute data
        >>> G.remove_edge(*e[:2]) # select first part of edge tuple
        """
        try:
            del self.adj[u][v]
            if u != v:  # self-loop needs only one entry removed
                del self.adj[v][u]
        except KeyError:
            raise NetworkXError("The edge %s-%s is not in the graph" % (u, v))

    def remove_edges_from(self, ebunch):
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            Each edge given in the list or container will be removed
            from the graph. The edges can be:

                - 2-tuples (u,v) edge between u and v.
                - 3-tuples (u,v,k) where k is ignored.

        See Also
        --------
        remove_edge : remove a single edge

        Notes
        -----
        Will fail silently if an edge in ebunch is not in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> ebunch=[(1,2),(2,3)]
        >>> G.remove_edges_from(ebunch)
        """
        adj = self.adj
        for e in ebunch:
            u, v = e[:2]  # ignore edge data if present
            if u in adj and v in adj[u]:
                del adj[u][v]
                if u != v:  # self loop needs only one entry removed
                    del adj[v][u]

    def has_edge(self, u, v):
        """Return True if the edge (u,v) is in the graph.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.

        Returns
        -------
        edge_ind : bool
            True if edge is in the graph, False otherwise.

        Examples
        --------
        Can be called either using two nodes u,v or edge tuple (u,v)

        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_edge(0,1)  # using two nodes
        True
        >>> e = (0,1)
        >>> G.has_edge(*e)  #  e is a 2-tuple (u,v)
        True
        >>> e = (0,1,{'weight':7})
        >>> G.has_edge(*e[:2])  # e is a 3-tuple (u,v,data_dictionary)
        True

        The following syntax are all equivalent:

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
        """Return an iterator over all neighbors of node n.

        Parameters
        ----------
        n : node
           A node in the graph

        Returns
        -------
        neighbors : iterator
            An iterator over all neighbors of node n

        Raises
        ------
        NetworkXError
            If the node n is not in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> [n for n in G.neighbors(0)]
        [1]

        Notes
        -----
        It is usually more convenient (and faster) to access the
        adjacency dictionary as ``G[n]``:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edge('a', 'b', weight=7)
        >>> G['a']
        {'b': {'weight': 7}}
        >>> G = nx.path_graph(4)
        >>> [n for n in G[0]]
        [1]
        """
        try:
            return iter(self.adj[n])
        except KeyError:
            raise NetworkXError("The node %s is not in the graph." % (n,))


    def edges(self, nbunch=None, data=False, default=None):
        """Return an iterator over the edges.

        Edges are returned as tuples with optional data
        in the order (node, neighbor, data).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u,v,ddict[data]).
            If True, return edge attribute dict in 3-tuple (u,v,ddict).
            If False, return 2-tuple (u,v).
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edges : iterator
            An iterator over (u,v) or (u,v,d) tuples of edges.

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.path_graph(3)   # or MultiGraph, etc
        >>> G.add_edge(2,3,weight=5)
        >>> [e for e in G.edges()]
        [(0, 1), (1, 2), (2, 3)]
        >>> list(G.edges(data=True))  # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges(data='weight', default=1))
        [(0, 1, 1), (1, 2, 1), (2, 3, 5)]
        >>> list(G.edges([0,3]))
        [(0, 1), (3, 2)]
        >>> list(G.edges(0))
        [(0, 1)]

        """
        seen = {}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n, nbrs in nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        yield (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            for n, nbrs in nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        d = ddict[data] if data in ddict else default
                        yield (n, nbr, d)
                seen[n] = 1
        else:  # data is False
            for n, nbrs in nodes_nbrs:
                for nbr in nbrs:
                    if nbr not in seen:
                        yield (n, nbr)
                seen[n] = 1
        del seen

    def get_edge_data(self, u, v, default=None):
        """Return the attribute dictionary associated with edge (u,v).

        Parameters
        ----------
        u, v : nodes
        default:  any Python object (default=None)
            Value to return if the edge (u,v) is not found.

        Returns
        -------
        edge_dict : dictionary
            The edge attribute dictionary.

        Notes
        -----
        It is faster to use G[u][v].

        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G[0][1]
        {}

        Warning: Assigning G[u][v] corrupts the graph data structure.
        But it is safe to assign attributes to that dictionary,

        >>> G[0][1]['weight'] = 7
        >>> G[0][1]['weight']
        7
        >>> G[1][0]['weight']
        7

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.get_edge_data(0, 1)  # default edge data is {}
        {}
        >>> e = (0,1)
        >>> G.get_edge_data(*e)  # tuple form
        {}
        >>> G.get_edge_data('a','b',default=0)  # edge not in graph, return 0
        0
        """
        try:
            return self.adj[u][v]
        except KeyError:
            return default

    def adjacency(self):
        """Return an iterator over (node, adjacency dict) tuples for all nodes.

        This is the fastest way to look at every edge.
        For directed graphs, only outgoing adjacencies are included.

        Returns
        -------
        adj_iter : iterator
           An iterator over (node, adjacency dictionary) for all nodes in
           the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> [(n,nbrdict) for n,nbrdict in G.adjacency()]
        [(0, {1: {}}), (1, {0: {}, 2: {}}), (2, {1: {}, 3: {}}), (3, {2: {}})]

        """
        return iter(self.adj.items())

    def degree(self, nbunch=None, weight=None):
        """Return an iterator for (node, degree) or degree for single node.

        The node degree is the number of edges adjacent to the node.
        This function returns the degree for a single node or an iterator
        for a bunch of nodes or if nothing is passed as argument.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.

        weight : string or None, optional (default=None)
           The edge attribute that holds the numerical value used
           as a weight.  If None, then each edge has weight 1.
           The degree is the sum of the edge weights adjacent to the node.

        Returns
        -------
        If a single node is requested
        deg : int
            Degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, degree).

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.degree(0)  # node 0 with degree 1
        1
        >>> list(G.degree([0,1]))
        [(0, 1), (1, 2)]
        """
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            nbrs = self.adj[nbunch]
            if weight is None:
                return len(nbrs) + (1 if nbunch in nbrs else 0) # handle self-loops
            return sum(dd.get(weight, 1) for nbr,dd in nbrs.items()) +\
                    (nbrs[nbunch].get(weight, 1) if nbunch in nbrs else 0)

        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if weight is None:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, len(nbrs) + (1 if n in nbrs else 0))  # return tuple (n,degree)
        else:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, sum((nbrs[nbr].get(weight, 1) for nbr in nbrs)) +
                        (nbrs[n].get(weight, 1) if n in nbrs else 0))
        return d_iter()

    def clear(self):
        """Remove all nodes and edges from the graph.

        This also removes the name, and all graph, node, and edge attributes.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.clear()
        >>> list(G.nodes())
        []
        >>> list(G.edges())
        []

        """
        self.name = ''
        self.adj.clear()
        self.node.clear()
        self.graph.clear()

    def copy(self, with_data=True):
        """Return a copy of the graph.

        All copies reproduce the graph structure, but data attributes
        may be handled in different ways. There are four types of copies
        of a graph that people might want.

        Deepcopy -- The default behavior is a "deepcopy" where the graph
        structure as well as all data attributes and any objects they might
        contain are copied. The entire graph object is new so that changes
        in the copy do not affect the original object.

        Data Reference (Shallow) -- For a shallow copy (with_data=False)
        the graph structure is copied but the edge, node and graph attribute
        dicts are references to those in the original graph. This saves
        time and memory but could cause confusion if you change an attribute
        in one graph and it changes the attribute in the other.

        Independent Shallow -- This copy creates new independent attribute
        dicts and then does a shallow copy of the attributes. That is, any
        attributes that are containers are shared between the new graph
        and the original. This type of copy is not enabled. Instead use:

            >>> G = nx.path_graph(5)
            >>> H = G.__class__(G)

        Fresh Data-- For fresh data, the graph structure is copied while
        new empty data attribute dicts are created. The resulting graph
        is independent of the original and it has no edge, node or graph
        attributes. Fresh copies are not enabled. Instead use:

            >>> H = G.__class__()
            >>> H.add_nodes_from(G)
            >>> H.add_edges_from(G.edges())

        See the Python copy module for more information on shallow
        and deep copies, http://docs.python.org/library/copy.html.

        Parameters
        ----------
        with_data : bool, optional (default=True)
            If True, the returned graph will have a deep copy of the
            graph, node, and edge attributes of this object. Otherwise,
            the returned graph will be a shallow copy.

        Returns
        -------
        G : Graph
            A copy of the graph.

        See Also
        --------
        to_directed: return a directed copy of the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> H = G.copy()

        """
        if with_data:
            return deepcopy(self)
        return self.subgraph(self)

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return False

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

        Warning: If you have subclassed Graph to use dict-like objects in the
        data structure, those changes do not transfer to the DiGraph
        created by this method.

        Examples
        --------
        >>> G = nx.Graph()  # or MultiGraph, etc
        >>> G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1), (1, 0)]

        If already directed, return a (deep) copy

        >>> G = nx.DiGraph()  # or MultiDiGraph, etc
        >>> G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1)]
        """
        from networkx import DiGraph
        G = DiGraph()
        G.name = self.name
        G.add_nodes_from(self)
        G.add_edges_from(((u, v, deepcopy(data))
            for u, nbrs in self.adjacency()
            for v, data in nbrs.items()))
        G.graph = deepcopy(self.graph)
        G.node = deepcopy(self.node)
        return G

    def to_undirected(self):
        """Return an undirected copy of the graph.

        Returns
        -------
        G : Graph/MultiGraph
            A deepcopy of the graph.

        See Also
        --------
        copy, add_edge, add_edges_from

        Notes
        -----
        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar G=DiGraph(D) which returns a
        shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, http://docs.python.org/library/copy.html.

        Examples
        --------
        >>> G = nx.path_graph(2)   # or MultiGraph, etc
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1), (1, 0)]
        >>> G2 = H.to_undirected()
        >>> list(G2.edges())
        [(0, 1)]
        """
        return deepcopy(self)

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
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> H = G.subgraph([0,1,2])
        >>> list(H.edges())
        [(0, 1), (1, 2)]
        """
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n] = self.node[n]
        # namespace shortcuts for speed
        H_adj = H.adj
        self_adj = self.adj
        # add nodes and edges (undirected method)
        # Note that changing this may affect the deep-ness of self.copy()
        for n in H.node:
            Hnbrs = H.adjlist_inner_dict_factory()
            H_adj[n] = Hnbrs
            for nbr, d in self_adj[n].items():
                if nbr in H_adj:
                    # add both representations of edge: n-nbr and nbr-n
                    Hnbrs[nbr] = d
                    H_adj[nbr][n] = d
        H.graph = self.graph
        return H

    def edge_subgraph(self, edges):
        """Returns the subgraph induced by the specified edges.

        The induced subgraph contains each edge in `edges` and each
        node incident to any one of those edges.

        Parameters
        ----------
        edges : iterable
            An iterable of edges in this graph.

        Returns
        -------
        G : Graph
            An edge-induced subgraph of this graph with the same edge
            attributes.

        Notes
        -----
        The graph, edge, and node attributes in the returned subgraph
        are references to the corresponding attributes in the original
        graph. Thus changes to the node or edge structure of the
        returned graph will not be reflected in the original graph, but
        changes to the attributes will.

        To create a subgraph with its own copy of the edge or node
        attributes, use::

            >>> nx.Graph(G.edge_subgraph(edges))  # doctest: +SKIP

        If edge attributes are containers, a deep copy of the attributes
        can be obtained using::

            >>> G.edge_subgraph(edges).copy()  # doctest: +SKIP

        Examples
        --------
        >>> G = nx.path_graph(5)
        >>> H = G.edge_subgraph([(0, 1), (3, 4)])
        >>> list(H.nodes())
        [0, 1, 3, 4]
        >>> list(H.edges())
        [(0, 1), (3, 4)]

        """
        H = self.__class__()
        adj = self.adj
        # Filter out edges that don't correspond to nodes in the graph.
        edges = ((u, v) for u, v in edges if u in adj and v in adj[u])
        for u, v in edges:
            # Copy the node attributes if they haven't been copied
            # already.
            if u not in H.node:
                H.node[u] = self.node[u]
            if v not in H.node:
                H.node[v] = self.node[v]
            # Create an entry in the adjacency dictionary for the
            # nodes u and v if they don't exist yet.
            if u not in H.adj:
                H.adj[u] = H.adjlist_inner_dict_factory()
            if v not in H.adj:
                H.adj[v] = H.adjlist_inner_dict_factory()
            # Copy the edge attributes.
            H.edge[u][v] = self.edge[u][v]
            H.edge[v][u] = self.edge[v][u]
        H.graph = self.graph
        return H

    def nodes_with_selfloops(self):
        """Returns an iterator over nodes with self loops.

        A node with a self loop has an edge with both ends adjacent
        to that node.

        Returns
        -------
        nodelist : iterator
            A iterator over nodes with self loops.

        See Also
        --------
        selfloop_edges, number_of_selfloops

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edge(1, 1)
        >>> G.add_edge(1, 2)
        >>> list(G.nodes_with_selfloops())
        [1]

        """
        return (n for n, nbrs in self.adj.items() if n in nbrs)

    def selfloop_edges(self, data=False, default=None):
        """Returns an iterator over selfloop edges.

        A selfloop edge has the same node at both ends.

        Parameters
        ----------
        data : string or bool, optional (default=False)
            Return selfloop edges as two tuples (u,v) (data=False)
            or three-tuples (u,v,datadict) (data=True)
            or three-tuples (u,v,datavalue) (data='attrname')
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edgeiter : iterator over edge tuples
            An iterator over all selfloop edges.

        See Also
        --------
        nodes_with_selfloops, number_of_selfloops

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> list(G.selfloop_edges())
        [(1, 1)]
        >>> list(G.selfloop_edges(data=True))
        [(1, 1, {})]
        """
        if data is True:
            return ((n, n, nbrs[n])
                    for n, nbrs in self.adj.items() if n in nbrs)
        elif data is not False:
            return ((n, n, nbrs[n].get(data, default))
                    for n, nbrs in self.adj.items() if n in nbrs)
        else:
            return ((n, n)
                    for n, nbrs in self.adj.items() if n in nbrs)

    def number_of_selfloops(self):
        """Return the number of selfloop edges.

        A selfloop edge has the same node at both ends.

        Returns
        -------
        nloops : int
            The number of selfloops.

        See Also
        --------
        nodes_with_selfloops, selfloop_edges

        Examples
        --------
        >>> G=nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> G.number_of_selfloops()
        1
        """
        return sum(1 for _ in self.selfloop_edges())

    def size(self, weight=None):
        """Return the number of edges or total of all edge weights.

        Parameters
        ----------
        weight : string or None, optional (default=None)
            The edge attribute that holds the numerical value used
            as a weight. If None, then each edge has weight 1.

        Returns
        -------
        size : numeric
            The number of edges or
            (if weight keyword is provided) the total weight sum.

            If weight is None, returns an int. Otherwise a float
            (or more general numeric if the weights are more general).

        See Also
        --------
        number_of_edges

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.size()
        3

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edge('a','b',weight=2)
        >>> G.add_edge('b','c',weight=4)
        >>> G.size()
        2
        >>> G.size(weight='weight')
        6.0
        """
        s = sum(d for v, d in self.degree(weight=weight))
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2

    def number_of_edges(self, u=None, v=None):
        """Return the number of edges between two nodes.

        Parameters
        ----------
        u, v : nodes, optional (default=all edges)
            If u and v are specified, return the number of edges between
            u and v. Otherwise return the total number of all edges.

        Returns
        -------
        nedges : int
            The number of edges in the graph.  If nodes `u` and `v` are
            specified return the number of edges between those nodes. If
            the graph is directed, this only returns the number of edges
            from `u` to `v`.

        See Also
        --------
        size

        Examples
        --------
        For undirected graphs, this method counts the total number of
        edges in the graph::

            >>> G = nx.path_graph(4)
            >>> G.number_of_edges()
            3

        If you specify two nodes, this counts the total number of edges
        joining the two nodes::

            >>> G.number_of_edges(0, 1)
            1

        For directed graphs, this method can count the total number of
        directed edges from `u` to `v`::

            >>> G = nx.DiGraph()
            >>> G.add_edge(0, 1)
            >>> G.add_edge(1, 0)
            >>> G.number_of_edges(0, 1)
            1

        """
        if u is None: return int(self.size())
        if v in self.adj[u]:
            return 1
        else:
            return 0

    def nbunch_iter(self, nbunch=None):
        """Return an iterator over nodes contained in nbunch that are
        also in the graph.

        The nodes in nbunch are checked for membership in the graph
        and if not are silently ignored.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.

        Returns
        -------
        niter : iterator
            An iterator over nodes in nbunch that are also in the graph.
            If nbunch is None, iterate over all nodes in the graph.

        Raises
        ------
        NetworkXError
            If nbunch is not a node or or sequence of nodes.
            If a node in nbunch is not hashable.

        See Also
        --------
        Graph.__iter__

        Notes
        -----
        When nbunch is an iterator, the returned iterator yields values
        directly from nbunch, becoming exhausted when nbunch is exhausted.

        To test whether nbunch is a single node, one can use
        "if nbunch in self:", even after processing with this routine.

        If nbunch is not a node or a (possibly empty) sequence/iterator
        or None, a :exc:`NetworkXError` is raised.  Also, if any object in
        nbunch is not hashable, a :exc:`NetworkXError` is raised.
        """
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(self.adj)
        elif nbunch in self:  # if nbunch is a single node
            bunch = iter([nbunch])
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist, adj):
                try:
                    for n in nlist:
                        if n in adj:
                            yield n
                except TypeError as e:
                    message = e.args[0]
                    # capture error for non-sequence/iterator nbunch.
                    if 'iter' in message:
                        raise NetworkXError(
                            "nbunch is not a node or a sequence of nodes.")
                    # capture error for unhashable node.
                    elif 'hashable' in message:
                        raise NetworkXError(
                            "Node {} in the sequence nbunch is not a valid node.".format(n))
                    else:
                        raise
            bunch = bunch_iter(nbunch, self.adj)
        return bunch
