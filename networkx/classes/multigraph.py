"""Base class for MultiGraph."""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from copy import deepcopy
import networkx as nx
from networkx.classes.graph import Graph
from networkx import NetworkXError
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'])


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
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.  If the corresponding optional Python
        packages are installed the data can also be a NumPy matrix
        or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    Graph
    DiGraph
    MultiDiGraph

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

    >>> G.add_nodes_from([2,3])
    >>> G.add_nodes_from(range(100,110))
    >>> H=nx.Graph()
    >>> H.add_path([0,1,2,3,4,5,6,7,8,9])
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
    are added automatically.  If an edge already exists, an additional
    edge is created and stored using a key to identify the edge.
    By default the key is the lowest unused integer.

    >>> G.add_edges_from([(4,5,dict(route=282)), (4,5,dict(route=37))])
    >>> G[4]
    {3: {0: {}}, 5: {0: {}, 1: {'route': 282}, 2: {'route': 37}}}

    **Attributes:**

    Each graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute
    dictionaries named graph, node and edge respectively.

    >>> G = nx.MultiGraph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from() or G.node

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')
    >>> G.node[1]
    {'time': '5pm'}
    >>> G.node[1]['room'] = 714
    >>> del G.node[1]['room'] # remove attribute
    >>> G.nodes(data=True)
    [(1, {'time': '5pm'}), (3, {'time': '2pm'})]

    Warning: adding a node to G.node does not add it to the graph.

    Add edge attributes using add_edge(), add_edges_from(), subscript
    notation, or G.edge.

    >>> G.add_edge(1, 2, weight=4.7 )
    >>> G.add_edges_from([(3,4),(4,5)], color='red')
    >>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
    >>> G[1][2][0]['weight'] = 4.7
    >>> G.edge[1][2][0]['weight'] = 4

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> len(G)  # number of nodes in graph
    5
    >>> G[1] # adjacency dict keyed by neighbor to edge attributes
    ...            # Note: you should not change this dict manually!
    {2: {0: {'weight': 4}, 1: {'color': 'blue'}}}

    The fastest way to traverse all edges of a graph is via
    adjacency_iter(), but the edges() method is often more convenient.

    >>> for n,nbrsdict in G.adjacency_iter():
    ...     for nbr,keydict in nbrsdict.items():
    ...        for key,eattr in keydict.items():
    ...            if 'weight' in eattr:
    ...                (n,nbr,key,eattr['weight'])
    (1, 2, 0, 4)
    (2, 1, 0, 4)
    (2, 3, 0, 8)
    (3, 2, 0, 8)
    >>> G.edges(data='weight', keys=True)
    [(1, 2, 0, 4), (1, 2, 1, None), (2, 3, 0, 8), (3, 4, 0, None), (4, 5, 0, None)]

    **Reporting:**

    Simple graph information is obtained using methods.
    Iterator versions of many reporting methods exist for efficiency.
    Methods exist for reporting nodes(), edges(), neighbors() and degree()
    as well as the number of nodes and edges.

    For details on these and other miscellaneous methods, see below.

    **Subclasses (Advanced):**

    The MultiGraph class uses a dict-of-dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency lists keyed by node.
    The next dict (adjlist) represents the adjacency list and holds
    edge_key dicts keyed by neighbor. The edge_key dict holds each edge_attr
    dict keyed by edge key. The inner dict (edge_attr) represents
    the edge data and holds edge attribute values keyed by attribute names.

    Each of these four dicts in the dict-of-dict-of-dict-of-dict
    structure can be replaced by a user defined dict-like object.
    In general, the dict-like features should be maintained but
    extra features can be added. To replace one of the dicts create
    a new graph class by changing the class(!) variable holding the
    factory for that dict-like structure. The variable names
    are node_dict_factory, adjlist_dict_factory, edge_key_dict_factory
    and edge_attr_dict_factory.

    node_dict_factory : function, (default: dict)
        Factory function to be used to create the outer-most dict
        in the data structure that holds adjacency lists keyed by node.
        It should require no arguments and return a dict-like object.

    adjlist_dict_factory : function, (default: dict)
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
    Create a multigraph object that tracks the order nodes are added.

    >>> from collections import OrderedDict
    >>> class OrderedGraph(nx.MultiGraph):
    ...    node_dict_factory = OrderedDict
    >>> G = OrderedGraph()
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1), (2,1), (1,1)) )
    >>> G.edges()
    [(2, 1), (2, 1), (2, 2), (1, 1)]

    Create a multgraph object that tracks the order nodes are added
    and for each node track the order that neighbors are added and for
    each neighbor tracks the order that multiedges are added.

    >>> class OrderedGraph(nx.MultiGraph):
    ...    node_dict_factory = OrderedDict
    ...    adjlist_dict_factory = OrderedDict
    ...    edge_key_dict_factory = OrderedDict
    >>> G = OrderedGraph()
    >>> G.add_nodes_from( (2,1) )
    >>> G.nodes()
    [2, 1]
    >>> G.add_edges_from( ((2,2), (2,1,2,{'weight':0.1}), (2,1,1,{'weight':0.2}), (1,1)) )
    >>> G.edges(keys=True)
    [(2, 2, 0), (2, 1, 2), (2, 1, 1), (1, 1, 0)]

    """
    # node_dict_factory=dict    # already assigned in Graph
    # adjlist_dict_factory=dict
    edge_key_dict_factory = dict
    # edge_attr_dict_factory=dict

    def __init__(self, data=None, **attr):
        self.edge_key_dict_factory = self.edge_key_dict_factory
        Graph.__init__(self, data, **attr)

    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by providing
        a dictionary with key/value pairs.  See examples below.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        key : hashable identifier, optional (default=lowest unused integer)
            Used to distinguish multiedges between a pair of nodes.
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
        To replace/update edge data, use the optional key argument
        to identify a unique edge.  Otherwise a new edge will be created.

        NetworkX algorithms designed for weighted graphs cannot use
        multigraphs directly because it is not clear how to handle
        multiedge weights.  Convert to Graph using edge attribute
        'weight' to enable weighted graph algorithms.

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
        >>> G.add_edge(1, 2, key=0, weight=4)   # update data for key=0
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.adj:
            self.adj[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.adj:
            self.adj[v] = self.adjlist_dict_factory()
            self.node[v] = {}
        if v in self.adj[u]:
            keydict = self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key = len(keydict)
                while key in keydict:
                    key += 1
            datadict = keydict.get(key, self.edge_attr_dict_factory())
            datadict.update(attr_dict)
            keydict[key] = datadict
        else:
            # selfloops work this way without special treatment
            if key is None:
                key = 0
            datadict = self.edge_attr_dict_factory()
            datadict.update(attr_dict)
            keydict = self.edge_key_dict_factory()
            keydict[key] = datadict
            self.adj[u][v] = keydict
            self.adj[v][u] = keydict

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges can be:

                - 2-tuples (u,v) or
                - 3-tuples (u,v,d) for an edge attribute dict d, or
                - 4-tuples (u,v,k,d) for an edge identified by key k

        attr_dict : dictionary, optional  (default= no attributes)
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

        Edge attributes specified in edges take precedence
        over attributes specified generally.

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
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
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
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple, 3-tuple or 4-tuple." % (e,))
            ddd = {}
            ddd.update(attr_dict)
            ddd.update(dd)
            self.add_edge(u, v, key, ddd)

    def remove_edge(self, u, v, key=None):
        """Remove an edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove an edge between nodes u and v.
        key : hashable identifier, optional (default=None)
            Used to distinguish multiple edges between a pair of nodes.
            If None remove a single (abritrary) edge between u and v.

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
        >>> G.add_path([0,1,2,3])
        >>> G.remove_edge(0,1)
        >>> e = (1,2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple

        For multiple edges

        >>> G = nx.MultiGraph()   # or MultiDiGraph, etc
        >>> G.add_edges_from([(1,2),(1,2),(1,2)])
        >>> G.remove_edge(1,2) # remove a single (arbitrary) edge

        For edges with keys

        >>> G = nx.MultiGraph()   # or MultiDiGraph, etc
        >>> G.add_edge(1,2,key='first')
        >>> G.add_edge(1,2,key='second')
        >>> G.remove_edge(1,2,key='second')

        """
        try:
            d = self.adj[u][v]
        except (KeyError):
            raise NetworkXError(
                "The edge %s-%s is not in the graph." % (u, v))
        # remove the edge with specified data
        if key is None:
            d.popitem()
        else:
            try:
                del d[key]
            except (KeyError):
                raise NetworkXError(
                    "The edge %s-%s with key %s is not in the graph." % (
                        u, v, key))
        if len(d) == 0:
            # remove the key entries if last edge
            del self.adj[u][v]
            if u!=v:  # check for selfloop
                del self.adj[v][u]

    def remove_edges_from(self, ebunch):
        """Remove all edges specified in ebunch.

        Parameters
        ----------
        ebunch: list or container of edge tuples
            Each edge given in the list or container will be removed
            from the graph. The edges can be:

                - 2-tuples (u,v) All edges between u and v are removed.
                - 3-tuples (u,v,key) The edge identified by key is removed.
                - 4-tuples (u,v,key,data) where data is ignored.

        See Also
        --------
        remove_edge : remove a single edge

        Notes
        -----
        Will fail silently if an edge in ebunch is not in the graph.

        Examples
        --------
        >>> G = nx.MultiGraph() # or MultiDiGraph
        >>> G.add_path([0,1,2,3])
        >>> ebunch=[(1,2),(2,3)]
        >>> G.remove_edges_from(ebunch)

        Removing multiple copies of edges

        >>> G = nx.MultiGraph()
        >>> G.add_edges_from([(1,2),(1,2),(1,2)])
        >>> G.remove_edges_from([(1,2),(1,2)])
        >>> G.edges()
        [(1, 2)]
        >>> G.remove_edges_from([(1,2),(1,2)]) # silently ignore extra copy
        >>> G.edges() # now empty graph
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
        Can be called either using two nodes u,v, an edge tuple (u,v),
        or an edge tuple (u,v,key).

        >>> G = nx.MultiGraph()   # or MultiDiGraph
        >>> G.add_path([0,1,2,3])
        >>> G.has_edge(0,1)  # using two nodes
        True
        >>> e = (0,1)
        >>> G.has_edge(*e)  #  e is a 2-tuple (u,v)
        True
        >>> G.add_edge(0,1,key='a')
        >>> G.has_edge(0,1,key='a')  # specify key
        True
        >>> e=(0,1,'a')
        >>> G.has_edge(*e) # e is a 3-tuple (u,v,'a')
        True

        The following syntax are equivalent:

        >>> G.has_edge(0,1)
        True
        >>> 1 in G[0]  # though this gives KeyError if 0 not in G
        True



        """
        try:
            if key is None:
                return v in self.adj[u]
            else:
                return key in self.adj[u][v]
        except KeyError:
            return False

    def edges(self, nbunch=None, data=False, keys=False, default=None):
        """Return a list of edges.

        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, key, data).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : bool, optional (default=False)
            Return two tuples (u,v) (False) or three-tuples (u,v,data) (True).
        keys : bool, optional (default=False)
            Return two tuples (u,v) (False) or three-tuples (u,v,key) (True).

        Returns
        --------
        edge_list: list of edge tuples
            Edges that are adjacent to any node in nbunch, or a list
            of all edges if nbunch is not specified.

        See Also
        --------
        edges_iter : return an iterator over the edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.MultiGraph()  # or MultiDiGraph
        >>> G.add_path([0,1,2])
        >>> G.add_edge(2,3,weight=5)
        >>> G.edges()
        [(0, 1), (1, 2), (2, 3)]
        >>> G.edges(data=True) # default edge data is {} (empty dictionary)
        [(0, 1, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges_iter(data='weight', default=1))
        [(0, 1, 1), (1, 2, 1), (2, 3, 5)]
        >>> G.edges(keys=True) # default keys are integers
        [(0, 1, 0), (1, 2, 0), (2, 3, 0)]
        >>> G.edges(data=True,keys=True) # default keys are integers
        [(0, 1, 0, {}), (1, 2, 0, {}), (2, 3, 0, {'weight': 5})]
        >>> list(G.edges(data='weight',default=1,keys=True))
        [(0, 1, 0, 1), (1, 2, 0, 1), (2, 3, 0, 5)]
        >>> G.edges([0,3])
        [(0, 1), (3, 2)]
        >>> G.edges(0)
        [(0, 1)]

        """
        return list(self.edges_iter(nbunch, data, keys, default))

    def edges_iter(self, nbunch=None, data=False, keys=False, default=None):
        """Return an iterator over the edges.

        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, key, data).

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
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edge_iter : iterator
            An iterator of (u,v), (u,v,d) or (u,v,key,d) tuples of edges.

        See Also
        --------
        edges : return a list of edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = nx.MultiGraph()   # or MultiDiGraph
        >>> G.add_path([0,1,2])
        >>> G.add_edge(2,3,weight=5)
        >>> [e for e in G.edges_iter()]
        [(0, 1), (1, 2), (2, 3)]
        >>> list(G.edges_iter(data=True)) # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (2, 3, {'weight': 5})]
        >>> list(G.edges_iter(data='weight', default=1))
        [(0, 1, 1), (1, 2, 1), (2, 3, 5)]
        >>> list(G.edges(keys=True)) # default keys are integers
        [(0, 1, 0), (1, 2, 0), (2, 3, 0)]
        >>> list(G.edges(data=True,keys=True)) # default keys are integers
        [(0, 1, 0, {}), (1, 2, 0, {}), (2, 3, 0, {'weight': 5})]
        >>> list(G.edges(data='weight',default=1,keys=True))
        [(0, 1, 0, 1), (1, 2, 0, 1), (2, 3, 0, 5)]
        >>> list(G.edges_iter([0,3]))
        [(0, 1), (3, 2)]
        >>> list(G.edges_iter(0))
        [(0, 1)]

        """
        seen = {}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            yield (n, nbr, key, ddict) if keys else (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            d = ddict[data] if data in ddict else default
                            yield (n, nbr, key, d) if keys else (n, nbr, d)
                seen[n] = 1
        else:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key in keydict:
                            yield (n, nbr, key) if keys else (n, nbr)
                seen[n] = 1
        del seen

    def get_edge_data(self, u, v, key=None, default=None):
        """Return the attribute dictionary associated with edge (u,v).

        Parameters
        ----------
        u, v : nodes

        default :  any Python object (default=None)
            Value to return if the edge (u,v) is not found.

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
        >>> G.add_edge(0,1,key='a',weight=7)
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
        >>> G.add_path([0,1,2,3])
        >>> G.get_edge_data(0,1)
        {0: {}}
        >>> e = (0,1)
        >>> G.get_edge_data(*e) # tuple form
        {0: {}}
        >>> G.get_edge_data('a','b',default=0) # edge not in graph, return 0
        0
        """
        try:
            if key is None:
                return self.adj[u][v]
            else:
                return self.adj[u][v][key]
        except KeyError:
            return default

    def degree_iter(self, nbunch=None, weight=None):
        """Return an iterator for (node, degree).

        The node degree is the number of edges adjacent to the node.

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
        nd_iter : an iterator
            The iterator returns two-tuples of (node, degree).

        See Also
        --------
        degree

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2,3])
        >>> list(G.degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.degree_iter([0,1]))
        [(0, 1), (1, 2)]

        """
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            for n, nbrs in nodes_nbrs:
                deg = sum([len(data) for data in nbrs.values()])
                yield (n, deg + (n in nbrs and len(nbrs[n])))
        else:
            # edge weighted graph - degree is sum of nbr edge weights
            for n, nbrs in nodes_nbrs:
                deg = sum([d.get(weight, 1)
                           for data in nbrs.values()
                           for d in data.values()])
                if n in nbrs:
                    deg += sum([d.get(weight, 1)
                                for key, d in nbrs[n].items()])
                yield (n, deg)

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return True

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return False

    def to_directed(self):
        """Return a directed representation of the graph.

        Returns
        -------
        G : MultiDiGraph
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

        Warning: If you have subclassed MultiGraph to use dict-like objects
        in the data structure, those changes do not transfer to the MultiDiGraph
        created by this method.

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
        from networkx.classes.multidigraph import MultiDiGraph
        G = MultiDiGraph()
        G.add_nodes_from(self)
        G.add_edges_from((u, v, key, deepcopy(datadict))
                            for u, nbrs in self.adjacency_iter()
                            for v, keydict in nbrs.items()
                            for key, datadict in keydict.items())
        G.graph = deepcopy(self.graph)
        G.node = deepcopy(self.node)
        return G

    def selfloop_edges(self, data=False, keys=False, default=None):
        """Return a list of selfloop edges.

        A selfloop edge has the same node at both ends.

        Parameters
        ----------
        data : bool, optional (default=False)
            Return selfloop edges as two tuples (u,v) (data=False)
            or three-tuples (u,v,datadict) (data=True)
            or three-tuples (u,v,datavalue) (data='attrname')
        default : value, optional (default=None)
            Value used for edges that dont have the requested attribute.
            Only relevant if data is not True or False.
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edgelist : list of edge tuples
            A list of all selfloop edges.

        See Also
        --------
        nodes_with_selfloops, number_of_selfloops

        Examples
        --------
        >>> G = nx.MultiGraph()   # or MultiDiGraph
        >>> G.add_edge(1,1)
        >>> G.add_edge(1,2)
        >>> G.selfloop_edges()
        [(1, 1)]
        >>> G.selfloop_edges(data=True)
        [(1, 1, {})]
        >>> G.selfloop_edges(keys=True)
        [(1, 1, 0)]
        >>> G.selfloop_edges(keys=True, data=True)
        [(1, 1, 0, {})]
        """
        if data is True:
            if keys:
                return [(n, n, k, d)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k, d in nbrs[n].items()]
            else:
                return [(n, n, d)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values()]
        elif data is not False:
            if keys:
                return [(n, n, k, d.get(data, default))
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k, d in nbrs[n].items()]
            else:
                return [(n, n, d.get(data, default))
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values()]
        else:
            if keys:
                return [(n, n, k)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k in nbrs[n].keys()]
            else:
                return [(n, n)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values()]

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
            The number of edges in the graph.  If nodes u and v are specified
            return the number of edges between those nodes.

        See Also
        --------
        size

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2,3])
        >>> G.number_of_edges()
        3
        >>> G.number_of_edges(0,1)
        1
        >>> e = (0,1)
        >>> G.number_of_edges(*e)
        1
        """
        if u is None: return self.size()
        try:
            edgedata = self.adj[u][v]
        except KeyError:
            return 0  # no such edge
        return len(edgedata)

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
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n] = self.node[n]
        # namespace shortcuts for speed
        H_adj = H.adj
        self_adj = self.adj
        # add nodes and edges (undirected method)
        for n in H:
            Hnbrs = H.adjlist_dict_factory()
            H_adj[n] = Hnbrs
            for nbr, edgedict in self_adj[n].items():
                if nbr in H_adj:
                    # add both representations of edge: n-nbr and nbr-n
                    # they share the same edgedict
                    ed = edgedict.copy()
                    Hnbrs[nbr] = ed
                    H_adj[nbr][n] = ed
        H.graph = self.graph
        return H
