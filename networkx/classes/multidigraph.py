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
"""Base class for MultiDiGraph."""
from copy import deepcopy

import networkx as nx
from networkx.classes.graph import Graph  # for doctests
from networkx.classes.digraph import DiGraph
from networkx.classes.multigraph import MultiGraph
from networkx.classes.views import AtlasView3
from networkx.classes.views import OutMultiEdgeView, InMultiEdgeView, \
        DiMultiDegreeView, OutMultiDegreeView, InMultiDegreeView
from networkx.exception import NetworkXError


class MultiDiGraph(MultiGraph, DiGraph):
    """A directed graph class that can store multiedges.

    Multiedges are multiple edges between two nodes.  Each edge
    can hold optional data or attributes.

    A MultiDiGraph holds directed edges.  Self loops are allowed.

    Nodes can be arbitrary (hashable) Python objects with optional
    key/value attributes.

    Edges are represented as links between nodes with optional
    key/value attributes.

    Parameters
    ----------
    incoming_graph_data : input graph (optional, default: None)
        Data to initialize graph. If None (default) an empty
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
    MultiGraph
    OrderedMultiDiGraph

    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and
    no edges.

    >>> G = nx.MultiDiGraph()

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

    >>> ekey = G.add_edge(1, 2)

    a list of edges,

    >>> ekeys = G.add_edges_from([(1, 2), (1, 3)])

    or a collection of edges,

    >>> ekeys = G.add_edges_from(H.edges())

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically.  If an edge already exists, an additional
    edge is created and stored using ekey to identify the edge.
    By default the ekey is the lowest unused integer.

    >>> ekeys = G.add_edges_from([(4,5,dict(route=282)), (4,5,dict(route=37))])
    >>> G[4]
    AtlasView2({5: {0: {}, 1: {'route': 282}, 2: {'route': 37}}})

    **Attributes:**

    Each graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute
    dictionaries named graph, node and edge respectively.

    >>> G = nx.MultiDiGraph(day="Friday")
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

    >>> ekey = G.add_edge(1, 2, weight=4.7 )
    >>> ekeys = G.add_edges_from([(3, 4), (4, 5)], color='red')
    >>> ekeys = G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
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
    AtlasView2({2: {0: {'weight': 4}, 1: {'color': 'blue'}}})

    The fastest way to traverse all edges of a graph is via
    adjacency():

    >>> for n, nbrsdict in G.adjacency():
    ...     for nbr, keydict in nbrsdict.items():
    ...        for ekey, eattr in keydict.items():
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

    The MultiDiGraph class uses a dict-of-dict-of-dict-of-dict structure.
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

    def __init__(self, incoming_graph_data=None, **attr):
        self.edge_key_dict_factory = self.edge_key_dict_factory
        DiGraph.__init__(self, incoming_graph_data, **attr)

    @property
    def edge(self):
        return OutMultiEdgeView(self)

    @property
    def adj(self):
        return AtlasView3(self._succ)

    @property
    def succ(self):
        return AtlasView3(self._succ)

    @property
    def pred(self):
        return AtlasView3(self._pred)

    def add_edge(self, u_for_edge, v_for_edge, ekey=None, **attr):
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
        ekey : hashable identifier, optional (default=lowest unused integer)
            Used to distinguish multiedges between a pair of nodes.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with the edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        Returns
        -------
        The edge ekey assigned to the edge.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        To replace/update edge data, use the optional ekey argument
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

        >>> G = nx.MultiDiGraph()
        >>> e = (1, 2)
        >>> ekey = G.add_edge(1, 2)    # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        1
        >>> G.add_edges_from( [(1, 2)] ) # add edges from iterable container
        [2]

        Associate data to edges using keywords:

        >>> ekey = G.add_edge(1, 2, weight=3)
        >>> ekey = G.add_edge(1, 2, ekey=0, weight=4)  # update data for edge
        >>> ekey = G.add_edge(1, 3, weight=7, capacity=15, length=342.7)

        For non-string associations, directly access the edge's attribute
        dictionary.
        """
        u, v = u_for_edge, v_for_edge
        # add nodes
        if u not in self._succ:
            self._succ[u] = self.adjlist_inner_dict_factory()
            self._pred[u] = self.adjlist_inner_dict_factory()
            self._node[u] = {}
        if v not in self._succ:
            self._succ[v] = self.adjlist_inner_dict_factory()
            self._pred[v] = self.adjlist_inner_dict_factory()
            self._node[v] = {}
        if ekey is None:
            ekey = self.new_edge_key(u, v)
        if v in self._succ[u]:
            keydict = self._adj[u][v]
            datadict = keydict.get(ekey, self.edge_key_dict_factory())
            datadict.update(attr)
            keydict[ekey] = datadict
        else:
            # selfloops work this way without special treatment
            datadict = self.edge_attr_dict_factory()
            datadict.update(attr)
            keydict = self.edge_key_dict_factory()
            keydict[ekey] = datadict
            self._succ[u][v] = keydict
            self._pred[v][u] = keydict
        return ekey

    def remove_edge(self, u, v, ekey=None):
        """Remove an edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove an edge between nodes u and v.
        ekey : hashable identifier, optional (default=None)
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
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.remove_edge(0, 1)
        >>> e = (1, 2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple

        For multiple edges

        >>> G = nx.MultiDiGraph()
        >>> G.add_edges_from([(1, 2), (1, 2), (1, 2)])  # key_list returned
        [0, 1, 2]
        >>> G.remove_edge(1, 2) # remove a single (arbitrary) edge

        For edges with keys

        >>> G = nx.MultiDiGraph()
        >>> G.add_edge(1, 2, ekey='first')
        'first'
        >>> G.add_edge(1, 2, ekey='second')
        'second'
        >>> G.remove_edge(1, 2, ekey='second')

        """
        try:
            d = self._adj[u][v]
        except KeyError:
            raise NetworkXError(
                "The edge %s-%s is not in the graph." % (u, v))
        # remove the edge with specified data
        if ekey is None:
            d.popitem()
        else:
            try:
                del d[ekey]
            except KeyError:
                msg = "The edge %s-%s with ekey %s is not in the graph."
                raise NetworkXError(msg % (u, v, ekey))
        if len(d) == 0:
            # remove the entries if last edge
            del self._succ[u][v]
            del self._pred[v][u]

    @property
    def edges(self):
        """Return an iterator over the edges.

        edges(self, nbunch=None, data=False, keys=False, default=None)

        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, ekey, data).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edge : iterator
            An iterator over (u, v), (u, v, d) or (u, v, ekey, d) edge tuples.

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2])
        >>> ekey = G.add_edge(2, 3, weight=5)
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
        >>> list(G.edges([0, 2]))
        [(0, 1), (2, 3)]
        >>> list(G.edges(0))
        [(0, 1)]

        See Also
        --------
        in_edges, out_edges
        """
        self.__dict__['edges'] = edges = OutMultiEdgeView(self)
        self.__dict__['out_edges'] = edges
        return edges

    # alias out_edges to edges
    out_edges = edges

    @property
    def in_edges(self):
        """Return an iterator over the incoming edges.

        in_edges(self, nbunch=None, data=False, keys=False, default=None)

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        in_edge : iterator
            An iterator over (u, v), (u, v, d) or (u, v, ekey, d) edge tuples.

        See Also
        --------
        edges : return an iterator over edges
        """
        self.__dict__['in_edges'] = in_edges = InMultiEdgeView(self)
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
           The degree is the sum of the edge weights.

        Returns
        -------
        If a single nodes is requested
        deg : int
            Degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, degree).

        See Also
        --------
        out_degree, in_degree

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.degree(0) # node 0 with degree 1
        1
        >>> list(G.degree([0, 1]))
        [(0, 1), (1, 2)]

        """
        self.__dict__['degree'] = degree = DiMultiDegreeView(self)
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
            Degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, in-degree).

        See Also
        --------
        degree, out_degree

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.in_degree(0) # node 0 with degree 0
        0
        >>> list(G.in_degree([0, 1]))
        [(0, 0), (1, 1)]

        """
        self.__dict__['in_degree'] = in_degree = InMultiDegreeView(self)
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
           The degree is the sum of the edge weights.

        Returns
        -------
        If a single node is requested
        deg : int
            Degree of the node

        OR if multiple nodes are requested
        nd_iter : iterator
            The iterator returns two-tuples of (node, out-degree).

        See Also
        --------
        degree, in_degree

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> nx.add_path(G, [0, 1, 2, 3])
        >>> G.out_degree(0) # node 0 with degree 1
        1
        >>> list(G.out_degree([0, 1]))
        [(0, 1), (1, 1)]

        """
        self.__dict__['out_degree'] = out_degree = OutMultiDegreeView(self)
        return out_degree

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return True

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return True

    def to_directed(self):
        """Return a directed copy of the graph.

        Returns
        -------
        G : MultiDiGraph
            A deepcopy of the graph.

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

        Examples
        --------
        >>> G = nx.Graph()   # or MultiGraph, etc
        >>> G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1), (1, 0)]

        If already directed, return a (deep) copy

        >>> G = nx.MultiDiGraph()
        >>> ekey = G.add_edge(0, 1)
        >>> H = G.to_directed()
        >>> list(H.edges())
        [(0, 1)]
        """
        return deepcopy(self)

    def to_undirected(self, reciprocal=False):
        """Return an undirected representation of the digraph.

        Parameters
        ----------
        reciprocal : bool (optional)
          If True only keep edges that appear in both directions
          in the original digraph.

        Returns
        -------
        G : MultiGraph
            An undirected graph with the same name and nodes and
            with edge (u, v, data) if either (u, v, data) or (v, u, data)
            is in the digraph.  If both edges exist in digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

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

        """
        H = MultiGraph()
        H.name = self.name
        H.add_nodes_from(self)
        if reciprocal is True:
            H.add_edges_from((u, v, ekey, deepcopy(data))
                             for u, nbrs in self.adjacency()
                             for v, keydict in nbrs.items()
                             for ekey, data in keydict.items()
                             if self.has_edge(v, u, ekey))
        else:
            H.add_edges_from((u, v, ekey, deepcopy(data))
                             for u, nbrs in self.adjacency()
                             for v, keydict in nbrs.items()
                             for ekey, data in keydict.items())
        H.graph = deepcopy(self.graph)
        H._node = deepcopy(self._node)
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
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> H = G.subgraph([0, 1, 2])
        >>> list(H.edges())
        [(0, 1), (1, 2)]
        """
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H._node[n] = self._node[n]
        # namespace shortcuts for speed
        H_succ = H._succ
        H_pred = H._pred
        self_succ = self._succ
        self_pred = self._pred
        # add nodes
        for n in H:
            H_succ[n] = H.adjlist_inner_dict_factory()
            H_pred[n] = H.adjlist_inner_dict_factory()
        # add edges
        for u in H_succ:
            Hnbrs = H_succ[u]
            for v, edgedict in self_succ[u].items():
                if v in H_succ:
                    # add both representations of edge: u-v and v-u
                    # they share the same edgedict
                    ed = edgedict.copy()
                    Hnbrs[v] = ed
                    H_pred[v][u] = ed
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

            >>> nx.MultiDiGraph(G.edge_subgraph(edges))  # doctest: +SKIP

        If edge attributes are containers, a deep copy of the attributes
        can be obtained using::

            >>> G.edge_subgraph(edges).copy()  # doctest: +SKIP

        Examples
        --------
        Get a subgraph induced by only those edges that have a certain
        attribute::

            >>> # Create a graph in which some edges are "good" and some "bad".
            >>> G = nx.MultiDiGraph()
            >>> ekey = G.add_edge(0, 1, ekey=0, good=True)
            >>> ekey = G.add_edge(0, 1, ekey=1, good=False)
            >>> ekey = G.add_edge(1, 2, ekey=0, good=False)
            >>> ekey = G.add_edge(1, 2, ekey=1, good=True)
            >>> # Keep only those edges that are marked as "good".
            >>> edges = G.edges(keys=True, data='good')
            >>> edges = ((u, v, k) for (u, v, k, good) in edges if good)
            >>> H = G.edge_subgraph(edges)
            >>> list(H.edges(keys=True, data=True))
            [(0, 1, 0, {'good': True}), (1, 2, 1, {'good': True})]

        """
        H = self.__class__()
        succ = self._succ

        # Filter out edges that don't correspond to nodes in the graph.
        def is_in_graph(u, v, k):
            return u in succ and v in succ[u] and k in succ[u][v]

        edges = (e for e in edges if is_in_graph(*e))
        for u, v, k in edges:
            # Copy the node attributes if they haven't been copied
            # already.
            if u not in H.node:
                H._node[u] = self._node[u]
            if v not in H.node:
                H._node[v] = self._node[v]
            # Create an entry in the successors and predecessors
            # dictionary for the nodes u and v if they don't exist yet.
            if u not in H._succ:
                H._succ[u] = H.adjlist_inner_dict_factory()
            if v not in H._pred:
                H._pred[v] = H.adjlist_inner_dict_factory()
            # Create an entry in the edge dictionary for the edges (u,
            # v) and (v, u) if the don't exist yet.
            if v not in H._succ[u]:
                H._succ[u][v] = H.edge_key_dict_factory()
            if u not in H._pred[v]:
                H._pred[v][u] = H.edge_key_dict_factory()
            # Copy the edge attributes.
            H._succ[u][v][k] = self._succ[u][v][k]
            H._pred[v][u][k] = self._pred[v][u][k]
        H.graph = self.graph
        return H

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
            H.add_nodes_from(self)
            H.add_edges_from((v, u, k, deepcopy(d)) for u, v, k, d
                             in self.edges(keys=True, data=True))
            H.graph = deepcopy(self.graph)
            H._node = deepcopy(self._node)
        else:
            self._pred, self._succ = self._succ, self._pred
            self._adj = self._succ
            H = self
        return H
