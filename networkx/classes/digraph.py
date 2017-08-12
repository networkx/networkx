#    Copyright (C) 2004-2017 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:   Aric Hagberg <hagberg@lanl.gov>
#            Dan Schult <dschult@colgate.edu>
#            Pieter Swart <swart@lanl.gov>
"""Base class for directed graphs."""
from copy import deepcopy

import networkx as nx
from networkx.classes.graph import Graph
from networkx.classes.coreviews import AdjacencyView
from networkx.classes.reportviews import OutEdgeView, InEdgeView, \
        DiDegreeView, InDegreeView, OutDegreeView
from networkx.exception import NetworkXError
import networkx.convert as convert


class DiGraph(Graph):
    """
    Base class for directed graphs.

    A DiGraph stores nodes and edges with optional data, or attributes.

    DiGraphs hold directed edges.  Self loops are allowed but multiple
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
    Graph
    MultiGraph
    MultiDiGraph
    OrderedDiGraph

    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and
    no edges.

    >>> G = nx.DiGraph()

    G can be grown in several ways.

    **Nodes:**

    Add one node at a time:

    >>> G.add_node(1)

    Add the nodes from any container (a list, dict, set or
    even the lines from a file or the nodes from another graph).

    >>> G.add_nodes_from([2, 3])
    >>> G.add_nodes_from(range(100, 110))
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

    >>> G.add_edges_from([(1, 2), (1, 3)])

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

    >>> G = nx.DiGraph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from() or G.nodes

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')
    >>> G.nodes[1]
    {'time': '5pm'}
    >>> G.nodes[1]['room'] = 714
    >>> del G.nodes[1]['room'] # remove attribute
    >>> list(G.nodes(data=True))
    [(1, {'time': '5pm'}), (3, {'time': '2pm'})]

    Add edge attributes using add_edge(), add_edges_from(), subscript
    notation, or G.edge.

    >>> G.add_edge(1, 2, weight=4.7 )
    >>> G.add_edges_from([(3, 4), (4, 5)], color='red')
    >>> G.add_edges_from([(1, 2, {'color':'blue'}), (2, 3, {'weight':8})])
    >>> G[1][2]['weight'] = 4.7
    >>> G.edge[1, 2]['weight'] = 4

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> len(G)  # number of nodes in graph
    5

    The fastest way to traverse all edges of a graph is via
    adjacency(), but the edges() method is often more convenient.

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
    holding the factory for that dict-like structure. The variable names are
    node_dict_factory, adjlist_inner_dict_factory, adjlist_outer_dict_factory,
    and edge_attr_dict_factory.

    node_dict_factory : function, (default: dict)
        Factory function to be used to create the dict containing node
        attributes, keyed by node id.
        It should require no arguments and return a dict-like object

    adjlist_outer_dict_factory : function, (default: dict)
        Factory function to be used to create the outer-most dict
        in the data structure that holds adjacency info keyed by node.
        It should require no arguments and return a dict-like object.

    adjlist_inner_dict_factory : function, optional (default: dict)
        Factory function to be used to create the adjacency list
        dict which holds edge data keyed by neighbor.
        It should require no arguments and return a dict-like object

    edge_attr_dict_factory : function, optional (default: dict)
        Factory function to be used to create the edge attribute
        dict which holds attrbute values keyed by attribute name.
        It should require no arguments and return a dict-like object.

    Examples
    --------

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


    Please see :mod:`~networkx.classes.ordered` for more examples of
    creating graph subclasses by overwriting the base class `dict` with
    a dictionary-like object.
    """
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
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G = nx.Graph(name='my graph')
        >>> e = [(1, 2), (2, 3), (3, 4)] # list of edges
        >>> G = nx.Graph(e)

        Arbitrary graph attribute pairs (key=value) may be assigned

        >>> G = nx.Graph(e, day="Friday")
        >>> G.graph
        {'day': 'Friday'}

        """
        self.node_dict_factory = ndf = self.node_dict_factory
        self.adjlist_outer_dict_factory = self.adjlist_outer_dict_factory
        self.adjlist_inner_dict_factory = self.adjlist_inner_dict_factory
        self.edge_attr_dict_factory = self.edge_attr_dict_factory

        self.root_graph = self
        self.graph = {}  # dictionary for graph attributes
        self._node = ndf()  # dictionary for node attributes
        # We store two adjacency lists:
        # the  predecessors of node n are stored in the dict self._pred
        # the successors of node n are stored in the dict self._succ=self._adj
        self._adj = ndf()  # empty adjacency dictionary
        self._pred = ndf()  # predecessor
        self._succ = self._adj  # successor

        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data, create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)

    @property
    def edge(self):
        return OutEdgeView(self)

    @property
    def adj(self):
        return AdjacencyView(self._succ)

    @property
    def succ(self):
        return AdjacencyView(self._succ)

    @property
    def pred(self):
        return AdjacencyView(self._pred)

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
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Use keywords set/change node attributes:

        >>> G.add_node(1, size=10)
        >>> G.add_node(3, weight=0.4, UTM=('13S', 382871, 3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        if n not in self._succ:
            self._succ[n] = self.adjlist_inner_dict_factory()
            self._pred[n] = self.adjlist_inner_dict_factory()
            self._node[n] = attr
        else:  # update attr even if node already exists
            self._node[n].update(attr)

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
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_nodes_from('Hello')
        >>> K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes(), key=str)
        [0, 1, 2, 'H', 'e', 'l', 'o']

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1, 2], size=10)
        >>> G.add_nodes_from([3, 4], weight=0.4)

        Use (node, attrdict) tuples to update attributes for specific
        nodes.

        >>> G.add_nodes_from([(1, dict(size=11)), (2, {'color':'blue'})])
        >>> G.nodes[1]['size']
        11
        >>> H = nx.Graph()
        >>> H.add_nodes_from(G.nodes(data=True))
        >>> H.nodes[1]['size']
        11

        """
        for n in nodes:
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self._succ,
            # while pre-2.7.5 ironpython throws on self._succ[n]
            try:
                if n not in self._succ:
                    self._succ[n] = self.adjlist_inner_dict_factory()
                    self._pred[n] = self.adjlist_inner_dict_factory()
                    self._node[n] = attr.copy()
                else:
                    self._node[n].update(attr)
            except TypeError:
                nn, ndict = n
                if nn not in self._succ:
                    self._succ[nn] = self.adjlist_inner_dict_factory()
                    self._pred[nn] = self.adjlist_inner_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self._node[nn] = newdict
                else:
                    olddict = self._node[nn]
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
        try:
            nbrs = self._succ[n]
            del self._node[n]
        except KeyError:  # NetworkXError if n not in self
            raise NetworkXError("The node %s is not in the digraph." % (n,))
        for u in nbrs:
            del self._pred[u][n]   # remove all edges n-u in digraph
        del self._succ[n]          # remove node from succ
        for u in self._pred[n]:
            del self._succ[u][n]   # remove all edges n-u in digraph
        del self._pred[n]          # remove node from pred

    def remove_nodes_from(self, nbunch):
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
        for n in nbunch:
            try:
                succs = self._succ[n]
                del self._node[n]
                for u in succs:
                    del self._pred[u][n]   # remove all edges n-u in digraph
                del self._succ[n]          # now remove node
                for u in self._pred[n]:
                    del self._succ[u][n]   # remove all edges n-u in digraph
                del self._pred[n]          # now remove node
            except KeyError:
                pass  # silent failure on remove

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
        The following all add the edge e=(1, 2) to graph G:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1, 2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1, 2)] ) # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)

        For non-string associations, directly access the edge's attribute
        dictionary.

        >>> G.add_edge(1, 2)
        >>> G[1][2].update({0: 5})
        """
        # add nodes
        if u not in self._succ:
            self._succ[u] = self.adjlist_inner_dict_factory()
            self._pred[u] = self.adjlist_inner_dict_factory()
            self._node[u] = {}
        if v not in self._succ:
            self._succ[v] = self.adjlist_inner_dict_factory()
            self._pred[v] = self.adjlist_inner_dict_factory()
            self._node[v] = {}
        # add the edge
        datadict = self._adj[u].get(v, self.edge_attr_dict_factory())
        datadict.update(attr)
        self._succ[u][v] = datadict
        self._pred[v][u] = datadict

    def add_edges_from(self, ebunch, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as 2-tuples (u, v) or
            3-tuples (u, v, d) where d is a dictionary containing edge data.
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
        >>> G.add_edges_from([(0, 1), (1, 2)]) # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label='WN2898')
        """
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
            elif ne == 2:
                u, v = e
                dd = {}
            else:
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,))
            if u not in self._succ:
                self._succ[u] = self.adjlist_inner_dict_factory()
                self._pred[u] = self.adjlist_inner_dict_factory()
                self._node[u] = {}
            if v not in self._succ:
                self._succ[v] = self.adjlist_inner_dict_factory()
                self._pred[v] = self.adjlist_inner_dict_factory()
                self._node[v] = {}
            datadict = self._adj[u].get(v, self.edge_attr_dict_factory())
            datadict.update(attr)
            datadict.update(dd)
            self._succ[u][v] = datadict
            self._pred[v][u] = datadict

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
        >>> G = nx.Graph()   # or DiGraph, etc
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.remove_edge(0, 1)
        >>> e = (1, 2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple
        >>> e = (2, 3, {'weight':7}) # an edge with attribute data
        >>> G.remove_edge(*e[:2]) # select first part of edge tuple
        """
        try:
            del self._succ[u][v]
            del self._pred[v][u]
        except KeyError:
            raise NetworkXError("The edge %s-%s not in graph." % (u, v))

    def remove_edges_from(self, ebunch):
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            Each edge given in the list or container will be removed
            from the graph. The edges can be:

                - 2-tuples (u, v) edge between u and v.
                - 3-tuples (u, v, k) where k is ignored.

        See Also
        --------
        remove_edge : remove a single edge

        Notes
        -----
        Will fail silently if an edge in ebunch is not in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> ebunch = [(1, 2), (2, 3)]
        >>> G.remove_edges_from(ebunch)
        """
        for e in ebunch:
            u, v = e[:2]  # ignore edge data
            if u in self._succ and v in self._succ[u]:
                del self._succ[u][v]
                del self._pred[v][u]

    def has_successor(self, u, v):
        """Return True if node u has successor v.

        This is true if graph has the edge u->v.
        """
        return (u in self._succ and v in self._succ[u])

    def has_predecessor(self, u, v):
        """Return True if node u has predecessor v.

        This is true if graph has the edge u<-v.
        """
        return (u in self._pred and v in self._pred[u])

    def successors(self, n):
        """Return an iterator over successor nodes of n.

        neighbors() and successors() are the same.
        """
        try:
            return iter(self._succ[n])
        except KeyError:
            raise NetworkXError("The node %s is not in the digraph." % (n,))

    # digraph definitions
    neighbors = successors

    def predecessors(self, n):
        """Return an iterator over predecessor nodes of n."""
        try:
            return iter(self._pred[n])
        except KeyError:
            raise NetworkXError("The node %s is not in the digraph." % (n,))

    @property
    def edges(self):
        """Return an iterator over the edges.

        Edges are returned as tuples with optional data
        in the order (node, neighbor, data).
        edges(self, nbunch=None, data=False, default=None)

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edge : iterator
            An iterator over (u, v) or (u, v, d) tuples of edges.

        See Also
        --------
        in_edges, out_edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.DiGraph()   # or MultiDiGraph, etc
        >>> nx.add_path(G, [0, 1, 2])
        >>> G.add_edge(2, 3, weight=5)
        >>> [e for e in G.edges()]
        [(0, 1), (1, 2), (2, 3)]
        >>> list(G.edges(data=True)) # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges(data='weight', default=1))
        [(0, 1, 1), (1, 2, 1), (2, 3, 5)]
        >>> list(G.edges([0, 2]))
        [(0, 1), (2, 3)]
        >>> list(G.edges(0))
        [(0, 1)]

        """
        self.__dict__['edges'] = edges = OutEdgeView(self)
        self.__dict__['out_edges'] = edges
        return edges

    # alias out_edges to edges
    out_edges = edges

    @property
    def in_edges(self):
        """Return an iterator over the incoming edges.

        in_edges(self, nbunch=None, data=False, default=None):

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        in_edge : iterator
            An iterator over (u, v) or (u, v, d) tuples of incoming edges.

        See Also
        --------
        edges : return an iterator over edges
        """
        self.__dict__['in_edges'] = in_edges = InEdgeView(self)
        return in_edges

    @property
    def degree(self):
        """Return an iterator for (node, degree) or degree for single node.
        degree(self, nbunch=None, weight=None)

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

        See Also
        --------
        in_degree, out_degree

        Examples
        --------
        >>> G = nx.DiGraph()   # or MultiDiGraph
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.degree(0) # node 0 with degree 1
        1
        >>> list(G.degree([0, 1]))
        [(0, 1), (1, 2)]

        """
        self.__dict__['degree'] = degree = DiDegreeView(self)
        return degree

    @property
    def in_degree(self):
        """Return an iterator for (node, in-degree) or in-degree for single node.

        in_degree(self, nbunch=None, weight=None)

        The node in-degree is the number of edges pointing in to the node.
        This function returns the in-degree for a single node or an iterator
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
            In-degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, in-degree).

        See Also
        --------
        degree, out_degree

        Examples
        --------
        >>> G = nx.DiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.in_degree(0) # node 0 with degree 0
        0
        >>> list(G.in_degree([0, 1]))
        [(0, 0), (1, 1)]

        """
        self.__dict__['in_degree'] = in_degree = InDegreeView(self)
        return in_degree

    @property
    def out_degree(self):
        """Return an iterator for (node, out-degree) or out-degree for single node.

        out_degree(self, nbunch=None, weight=None)

        The node out-degree is the number of edges pointing out of the node.
        This function returns the out-degree for a single node or an iterator
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
            Out-degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, out-degree).

        See Also
        --------
        degree, in_degree

        Examples
        --------
        >>> G = nx.DiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.out_degree(0) # node 0 with degree 1
        1
        >>> list(G.out_degree([0, 1]))
        [(0, 1), (1, 1)]

        """
        self.__dict__['out_degree'] = out_degree = OutDegreeView(self)
        return out_degree

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
        self._succ.clear()
        self._pred.clear()
        self._node.clear()
        self.graph.clear()

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return True

    def fresh_copy(self):
        """Return a fresh copy graph with the same data structure."""
        return nx.DiGraph()

    def copy(self, as_view=False):
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
        if as_view is True:
            return nx.graphviews.DiGraphView(self)
        G = self.fresh_copy()
        G.graph.update(self.graph)
        G.add_nodes_from((n, d.copy()) for n, d in self._node.items())
        G.add_edges_from((u, v, datadict.copy())
                         for u, nbrs in self.adj.items()
                         for v, datadict in nbrs.items())
        return G

    def to_undirected(self, reciprocal=False, as_view=False):
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
            with edge (u, v, data) if either (u, v, data) or (v, u, data)
            is in the digraph.  If both edges exist in digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

        Notes
        -----
        If edges in both directions (u, v) and (v, u) exist in the
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

        Warning: If you have subclassed DiGraph to use dict-like objects
        in the data structure, those changes do not transfer to the
        Graph created by this method.
        """
        if as_view is True:
            return nx.graphviews.GraphView(self)
        # deepcopy when not a view
        G = Graph()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        if reciprocal is True:
            G.add_edges_from((u, v, deepcopy(d))
                             for u, nbrs in self.adj.items()
                             for v, d in nbrs.items()
                             if v in self._pred[u])
        else:
            G.add_edges_from((u, v, deepcopy(d))
                             for u, nbrs in self.adj.items()
                             for v, d in nbrs.items())
        return G

    def subgraph(self, nbunch):
        """Return a SubGraph view of the subgraph induced on nodes in nbunch.

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
        >>> H = G.subgraph([0, 1, 2])
        >>> list(H.edges())
        [(0, 1), (1, 2)]
        """
        induced_nodes = nx.filters.show_nodes(self.nbunch_iter(nbunch))
        return nx.graphviews.SubDiGraph(self, induced_nodes)

    def reverse(self, copy=True):
        """Return the reverse of the graph.

        The reverse is a graph with the same nodes and edges
        but with the directions of the edges reversed.

        Parameters
        ----------
        copy : bool optional (default=True)
            If True, return a new DiGraph holding the reversed edges.
            If False, reverse the reverse graph is created using
            the original graph (this changes the original graph).
        """
        if copy:
            H = self.__class__(name="Reverse of (%s)" % self.name)
            H.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
            H.add_edges_from((v, u, deepcopy(d)) for u, v, d
                             in self.edges(data=True))
            H.graph.update(deepcopy(self.graph))
            return H
        return nx.graphviews.ReverseView(self)
