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
"""Base class for MultiGraph."""
from copy import deepcopy

import networkx as nx
from networkx.classes.graph import Graph
from networkx.classes.coreviews import MultiAdjacencyView
from networkx.classes.reportviews import MultiEdgeView, MultiDegreeView
from networkx import NetworkXError
from networkx.utils import iterable


class MultiGraph(Graph):
    """
    An undirected graph class that can store multiedges.

    Multiedges are multiple edges between two nodes.  Each edge
    can hold optional data or attributes.

    A MultiGraph holds undirected edges.  Self loops are allowed.

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
    DiGraph
    MultiDiGraph
    OrderedMultiGraph

    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and
    no edges.

    >>> G = nx.MultiGraph()

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

    >>> key = G.add_edge(1, 2)

    a list of edges,

    >>> keys = G.add_edges_from([(1, 2), (1, 3)])

    or a collection of edges,

    >>> keys = G.add_edges_from(list(H.edges()))

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically.  If an edge already exists, an additional
    edge is created and stored using a key to identify the edge.
    By default the key is the lowest unused integer.

    >>> keys = G.add_edges_from([(4,5,{'route':28}), (4,5,{'route':37})])
    >>> G[4]
    AdjacencyView({3: {0: {}}, 5: {0: {}, 1: {'route': 28}, 2: {'route': 37}}})

    **Attributes:**

    Each graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute
    dictionaries named graph, node and edge respectively.

    >>> G = nx.MultiGraph(day="Friday")
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

    >>> key = G.add_edge(1, 2, weight=4.7 )
    >>> keys = G.add_edges_from([(3, 4), (4, 5)], color='red')
    >>> keys = G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
    >>> G[1][2][0]['weight'] = 4.7
    >>> G.edge[1, 2, 0]['weight'] = 4

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> len(G)  # number of nodes in graph
    5
    >>> G[1] # adjacency dict-like view keyed by neighbor to edge attributes
    AdjacencyView({2: {0: {'weight': 4}, 1: {'color': 'blue'}}})

    The fastest way to traverse all edges of a graph is via
    adjacency():

    >>> for n, nbrsdict in G.adjacency():
    ...     for nbr, keydict in nbrsdict.items():
    ...        for key, eattr in keydict.items():
    ...            if 'weight' in eattr:
    ...                # Do something useful with the edges
    ...                pass

    But the edges() method is often more convenient:

    >>> for u, v, keys, weight in G.edges(data='weight', keys=True):
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

    The MultiGraph class uses a dict-of-dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency information keyed by node.
    The next dict (adjlist_dict) represents the adjacency information and holds
    edge_key dicts keyed by neighbor. The edge_key dict holds each edge_attr
    dict keyed by edge key. The inner dict (edge_attr_dict) represents
    the edge data and holds edge attribute values keyed by attribute names.

    Each of these four dicts in the dict-of-dict-of-dict-of-dict
    structure can be replaced by a user defined dict-like object.
    In general, the dict-like features should be maintained but
    extra features can be added. To replace one of the dicts create
    a new graph class by changing the class(!) variable holding the
    factory for that dict-like structure. The variable names are
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

    adjlist_inner_dict_factory : function, (default: dict)
        Factory function to be used to create the adjacency list
        dict which holds multiedge key dicts keyed by neighbor.
        It should require no arguments and return a dict-like object.

    edge_key_dict_factory : function, (default: dict)
        Factory function to be used to create the edge key dict
        which holds edge data keyed by edge key.
        It should require no arguments and return a dict-like object.

    edge_attr_dict_factory : function, (default: dict)
        Factory function to be used to create the edge attribute
        dict which holds attrbute values keyed by attribute name.
        It should require no arguments and return a dict-like object.

    Examples
    --------

    Please see :mod:`~networkx.classes.ordered` for examples of
    creating graph subclasses by overwriting the base class `dict` with
    a dictionary-like object.
    """
    # node_dict_factory = dict    # already assigned in Graph
    # adjlist_outer_dict_factory = dict
    # adjlist_inner_dict_factory = dict
    edge_key_dict_factory = dict
    # edge_attr_dict_factory = dict

    def __init__(self, data=None, **attr):
        self.edge_key_dict_factory = self.edge_key_dict_factory
        Graph.__init__(self, data, **attr)

    @property
    def edge(self):
        return MultiEdgeView(self)

    @property
    def adj(self):
        return MultiAdjacencyView(self._adj)

    def new_edge_key(self, u, v):
        """Return an unused key for edges between nodes `u` and `v`.

        The nodes `u` and `v` do not need to be already in the graph.

        Notes
        -----

        In the standard MultiGraph class the new key is the number of existing
        edges between `u` and `v` (increased if necessary to ensure unused).
        The first edge will have key 0, then 1, etc. If an edge is removed
        further new_edge_keys may not be in this order.

        Parameters
        ----------
        u, v : nodes

        Returns
        -------
        key : int
        """
        try:
            keydict = self._adj[u][v]
        except KeyError:
            return 0
        key = len(keydict)
        while key in keydict:
            key += 1
        return key

    def add_edge(self, u, v, key=None, **attr):
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
        key : hashable identifier, optional (default=lowest unused integer)
            Used to distinguish multiedges between a pair of nodes.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        Returns
        -------
        The edge key assigned to the edge.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        To replace/update edge data, use the optional key argument
        to identify a unique edge.  Otherwise a new edge will be created.

        NetworkX algorithms designed for weighted graphs cannot use
        multigraphs directly because it is not clear how to handle
        multiedge weights.  Convert to Graph using edge attribute
        'weight' to enable weighted graph algorithms.

        Default keys are generated using the method `new_edge_key()`.
        This method can be overridden by subclassing the base class and
        providing a custom `new_edge_key()` method.

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
        >>> G.add_edge(1, 2, key=0, weight=4)   # update data for key=0
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # add nodes
        if u not in self._adj:
            self._adj[u] = self.adjlist_inner_dict_factory()
            self._node[u] = {}
        if v not in self._adj:
            self._adj[v] = self.adjlist_inner_dict_factory()
            self._node[v] = {}
        if key is None:
            key = self.new_edge_key(u, v)
        if v in self._adj[u]:
            keydict = self._adj[u][v]
            datadict = keydict.get(key, self.edge_attr_dict_factory())
            datadict.update(attr)
            keydict[key] = datadict
        else:
            # selfloops work this way without special treatment
            datadict = self.edge_attr_dict_factory()
            datadict.update(attr)
            keydict = self.edge_key_dict_factory()
            keydict[key] = datadict
            self._adj[u][v] = keydict
            self._adj[v][u] = keydict
        return key

    def add_edges_from(self, ebunch, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges can be:

                - 2-tuples (u, v) or
                - 3-tuples (u, v, d) for an edge data dict d, or
                - 3-tuples (u, v, k) for not iterable key k, or
                - 4-tuples (u, v, k, d) for an edge with data and key k

        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        Returns
        -------
        A list of edge keys assigned to the edges in `ebunch`.

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

        Default keys are generated using the method ``new_edge_key()``.
        This method can be overridden by subclassing the base class and
        providing a custom ``new_edge_key()`` method.

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
        keylist = []
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 4:
                u, v, key, dd = e
            elif ne == 3:
                u, v, dd = e
                key = None
            elif ne == 2:
                u, v = e
                dd = {}
                key = None
            else:
                msg = "Edge tuple {} must be a 2-tuple, 3-tuple or 4-tuple."
                raise NetworkXError(msg.format(e))
            ddd = {}
            ddd.update(attr)
            try:
                ddd.update(dd)
            except:
                if ne != 3:
                    raise
                key = dd
            key = self.add_edge(u, v, key)
            self[u][v][key].update(ddd)
            keylist.append(key)
        return keylist

    def remove_edge(self, u, v, key=None):
        """Remove an edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove an edge between nodes u and v.
        key : hashable identifier, optional (default=None)
            Used to distinguish multiple edges between a pair of nodes.
            If None remove a single (arbitrary) edge between u and v.

        Raises
        ------
        NetworkXError
            If there is not an edge between u and v, or
            if there is no edge with the specified key.

        See Also
        --------
        remove_edges_from : remove a collection of edges

        Examples
        --------
        >>> G = nx.MultiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.remove_edge(0, 1)
        >>> e = (1, 2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple

        For multiple edges

        >>> G = nx.MultiGraph()   # or MultiDiGraph, etc
        >>> G.add_edges_from([(1, 2), (1, 2), (1, 2)])  # key_list returned
        [0, 1, 2]
        >>> G.remove_edge(1, 2) # remove a single (arbitrary) edge

        For edges with keys

        >>> G = nx.MultiGraph()   # or MultiDiGraph, etc
        >>> G.add_edge(1, 2, key='first')
        'first'
        >>> G.add_edge(1, 2, key='second')
        'second'
        >>> G.remove_edge(1, 2, key='second')

        """
        try:
            d = self._adj[u][v]
        except KeyError:
            raise NetworkXError(
                "The edge %s-%s is not in the graph." % (u, v))
        # remove the edge with specified data
        if key is None:
            d.popitem()
        else:
            try:
                del d[key]
            except KeyError:
                msg = "The edge %s-%s with key %s is not in the graph."
                raise NetworkXError(msg % (u, v, key))
        if len(d) == 0:
            # remove the key entries if last edge
            del self._adj[u][v]
            if u != v:  # check for selfloop
                del self._adj[v][u]

    def remove_edges_from(self, ebunch):
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            Each edge given in the list or container will be removed
            from the graph. The edges can be:

                - 2-tuples (u, v) All edges between u and v are removed.
                - 3-tuples (u, v, key) The edge identified by key is removed.
                - 4-tuples (u, v, key, data) where data is ignored.

        See Also
        --------
        remove_edge : remove a single edge

        Notes
        -----
        Will fail silently if an edge in ebunch is not in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> ebunch=[(1, 2), (2, 3)]
        >>> G.remove_edges_from(ebunch)

        Removing multiple copies of edges

        >>> G = nx.MultiGraph()
        >>> keys = G.add_edges_from([(1, 2), (1, 2), (1, 2)])
        >>> G.remove_edges_from([(1, 2), (1, 2)])
        >>> list(G.edges())
        [(1, 2)]
        >>> G.remove_edges_from([(1, 2), (1, 2)]) # silently ignore extra copy
        >>> list(G.edges()) # now empty graph
        []
        """
        for e in ebunch:
            try:
                self.remove_edge(*e[:3])
            except NetworkXError:
                pass

    def has_edge(self, u, v, key=None):
        """Return True if the graph has an edge between nodes u and v.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.

        key : hashable identifier, optional (default=None)
            If specified return True only if the edge with
            key is found.

        Returns
        -------
        edge_ind : bool
            True if edge is in the graph, False otherwise.

        Examples
        --------
        Can be called either using two nodes u, v, an edge tuple (u, v),
        or an edge tuple (u, v, key).

        >>> G = nx.MultiGraph()   # or MultiDiGraph
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.has_edge(0, 1)  # using two nodes
        True
        >>> e = (0, 1)
        >>> G.has_edge(*e)  #  e is a 2-tuple (u, v)
        True
        >>> G.add_edge(0, 1, key='a')
        'a'
        >>> G.has_edge(0, 1, key='a')  # specify key
        True
        >>> e=(0, 1, 'a')
        >>> G.has_edge(*e) # e is a 3-tuple (u, v, 'a')
        True

        The following syntax are equivalent:

        >>> G.has_edge(0, 1)
        True
        >>> 1 in G[0]  # though this gives :exc:`KeyError` if 0 not in G
        True



        """
        try:
            if key is None:
                return v in self._adj[u]
            else:
                return key in self._adj[u][v]
        except KeyError:
            return False

    @property
    def edges(self):
        """Return an iterator over the edges.

        edges(self, nbunch=None, data=False, keys=False, default=None)

        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, key, data).

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
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edge : iterator
            An iterator over (u, v), (u, v, d) or (u, v, key, d) edge tuples

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.MultiGraph()   # or MultiDiGraph
        >>> nx.add_path(G, [0, 1, 2])
        >>> key = G.add_edge(2, 3, weight=5)
        >>> [e for e in G.edges()]
        [(0, 1), (1, 2), (2, 3)]
        >>> list(G.edges(data=True)) # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges(data='weight', default=1))
        [(0, 1, 1), (1, 2, 1), (2, 3, 5)]
        >>> list(G.edges(keys=True)) # default keys are integers
        [(0, 1, 0), (1, 2, 0), (2, 3, 0)]
        >>> list(G.edges(data=True, keys=True)) # default keys are integers
        [(0, 1, 0, {}), (1, 2, 0, {}), (2, 3, 0, {'weight': 5})]
        >>> list(G.edges(data='weight', default=1, keys=True))
        [(0, 1, 0, 1), (1, 2, 0, 1), (2, 3, 0, 5)]
        >>> list(G.edges([0, 3]))
        [(0, 1), (3, 2)]
        >>> list(G.edges(0))
        [(0, 1)]
        """
        self.__dict__['edges'] = edges = MultiEdgeView(self)
        return edges

    def get_edge_data(self, u, v, key=None, default=None):
        """Return the attribute dictionary associated with edge (u, v).

        Parameters
        ----------
        u, v : nodes

        default :  any Python object (default=None)
            Value to return if the edge (u, v) is not found.

        key : hashable identifier, optional (default=None)
            Return data only for the edge with specified key.

        Returns
        -------
        edge_dict : dictionary
            The edge attribute dictionary.

        Notes
        -----
        It is faster to use G[u][v][key].

        >>> G = nx.MultiGraph() # or MultiDiGraph
        >>> key = G.add_edge(0, 1, key='a', weight=7)
        >>> G[0][1]['a']  # key='a'
        {'weight': 7}

        Warning: Assigning G[u][v][key] corrupts the graph data structure.
        But it is safe to assign attributes to that dictionary,

        >>> G[0][1]['a']['weight'] = 10
        >>> G[0][1]['a']['weight']
        10
        >>> G[1][0]['a']['weight']
        10

        Examples
        --------
        >>> G = nx.MultiGraph() # or MultiDiGraph
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.get_edge_data(0, 1)
        {0: {}}
        >>> e = (0, 1)
        >>> G.get_edge_data(*e) # tuple form
        {0: {}}
        >>> G.get_edge_data('a', 'b', default=0) # edge not in graph, return 0
        0
        """
        try:
            if key is None:
                return self._adj[u][v]
            else:
                return self._adj[u][v][key]
        except KeyError:
            return default

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
            Degree of the node, if a single node is passed as argument.

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, degree).

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.degree(0) # node 0 with degree 1
        1
        >>> list(G.degree([0, 1]))
        [(0, 1), (1, 2)]

        """
        self.__dict__['degree'] = degree = MultiDegreeView(self)
        return degree

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return True

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return False

    def fresh_copy(self):
        """Return a fresh copy graph with the same data structure."""
        return nx.MultiGraph()

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
            return nx.graphviews.MultiGraphView(self)
        G = self.fresh_copy()
        G.graph.update(self.graph)
        G.add_nodes_from((n, d.copy()) for n, d in self._node.items())
        G.add_edges_from((u, v, key, datadict.copy())
                         for u, nbrs in self.adj.items()
                         for v, keydict in nbrs.items()
                         for key, datadict in keydict.items())
        return G

    def to_directed(self, as_view=False):
        """Return a directed representation of the graph.

        Returns
        -------
        G : MultiDiGraph
            A directed graph with the same name, same nodes, and with
            each edge (u, v, data) replaced by two directed edges
            (u, v, data) and (v, u, data).

        Notes
        -----
        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar D=DiGraph(G) which returns a
        shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, http://docs.python.org/library/copy.html.

        Warning: If you have subclassed MultiGraph to use dict-like objects
        in the data structure, those changes do not transfer to the
        MultiDiGraph created by this method.

        Examples
        --------
        >>> G = nx.Graph()   # or MultiGraph, etc
        >>> G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1), (1, 0)]

        If already directed, return a (deep) copy

        >>> G = nx.DiGraph()   # or MultiDiGraph, etc
        >>> G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1)]
        """
        if as_view is True:
            return nx.graphviews.MultiDiGraphView(self)
        # deepcopy when not a view
        from networkx.classes.multidigraph import MultiDiGraph
        G = MultiDiGraph()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from((u, v, key, deepcopy(datadict))
                         for u, nbrs in self.adjacency()
                         for v, keydict in nbrs.items()
                         for key, datadict in keydict.items())
        return G

    def to_undirected(self, as_view=False):
        if as_view is True:
            return nx.graphviews.MultiGraphView(self)
        # deepcopy when not a view
        G = MultiGraph()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from((u, v, key, deepcopy(datadict))
                         for u, nbrs in self.adj.items()
                         for v, keydict in nbrs.items()
                         for key, datadict in keydict.items())
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
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> H = G.subgraph([0, 1, 2])
        >>> list(H.edges())
        [(0, 1), (1, 2)]
        """
        induced_nodes = nx.filters.show_nodes(self.nbunch_iter(nbunch))
        return nx.graphviews.SubMultiGraph(self, induced_nodes)

    def number_of_edges(self, u=None, v=None):
        """Return the number of edges between two nodes.

        Parameters
        ----------
        u, v : nodes, optional (Gefault=all edges)
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
        For undirected multigraphs, this method counts the total number
        of edges in the graph::

            >>> G = nx.MultiGraph()
            >>> G.add_edges_from([(0, 1), (0, 1), (1, 2)])
            [0, 1, 0]
            >>> G.number_of_edges()
            3

        If you specify two nodes, this counts the total number of edges
        joining the two nodes::

            >>> G.number_of_edges(0, 1)
            2

        For directed multigraphs, this method can count the total number
        of directed edges from `u` to `v`::

            >>> G = nx.MultiDiGraph()
            >>> G.add_edges_from([(0, 1), (0, 1), (1, 0)])
            [0, 1, 0]
            >>> G.number_of_edges(0, 1)
            2
            >>> G.number_of_edges(1, 0)
            1

        """
        if u is None:
            return self.size()
        try:
            edgedata = self._adj[u][v]
        except KeyError:
            return 0  # no such edge
        return len(edgedata)
