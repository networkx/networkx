from copy import deepcopy
from functools import cached_property

import networkx as nx
from networkx.classes.reportviews import NodeView
from networkx.exception import NetworkXError

__all__ = ["MixedEdgeGraph"]


class MixedEdgeGraph:
    """Base class for mixed-edge graphs.

    A mixed-edge graph stores nodes and different kinds of edges using a
    composition of networkx graphs.

    The edges can represent non-directed (i.e. `networkx.Graph`), or
    directed (i.e. `networkx.DiGraph`) edge connections among nodes. Nodes can be
    any nodes that can be represented in `networkx.Graph`, and `networkx.DiGraph`.

    Edges are represented as links between nodes with optional
    key/value attributes.

    .. warning:: MixedEdgeGraph is an experimental feature that is subject to change
        without deprecation. Please use with caution.

    Parameters
    ----------
    graphs : List of Graph | DiGraph
        A list of networkx single-edge graphs.
    edge_types : List of str
        A list of names for each edge type.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    networkx.Graph
    networkx.DiGraph
    networkx.MultiGraph
    networkx.MultiDiGraph

    Notes
    -----
    Besides the changes mentioned below, a ``MixedEdgeGraph`` matches
    the entire API provided by the Graph/DiGraph classes.

    **Changes compared to existing networkx graphs:**

    Compared to `networkx.Graph` and `networkx.DiGraph`, a ``MixedEdgeGraph`` has
    a different method for initializing the graph and adding edges.
    When adding/removing/update edges to the graph, if that edge type
    does not exist, then an error will be raised. Users should explicitly
    add an edge type graph via the ``add_edge_type`` function.

    Moreover, computing an ``edge_subgraph`` is not supported for
    ``MixedEdgeGraph``.

    **Edges, Adjacencies and Degree:**

    Compared to single-edge networkx graphs, ``MixedEdgeGraph`` implements
    these as functions rather than cached properties.

    **Neighbors:**
    Compared to single-edge graphs, neighbors in a ``MixedEdgeGraph`` of a node is
    defined as any other node with an edge connected to the node that is being checked.

    **Keywords:**
    Since ``MixedEdgeGraph`` comprises of possibly many different edge types.
    In the API, there are a few keywords: 'any' or 'all'. Within the API, 'any'
    means any edge type, whereas 'all' refers to all edge types.
    """

    _graphs = list
    graph_attr_dict_factory = dict
    node_dict_factory = dict
    node_attr_dict_factory = dict

    def __init__(self, graphs=None, edge_types=None, **attr):
        if any(x is not None for x in [graphs, edge_types]):
            if not all(x is not None for x in [graphs, edge_types]):
                raise RuntimeError(
                    "If graphs or edge types are defined, then they both must be defined."
                )
            if len(graphs) != len(edge_types):
                raise RuntimeError(
                    f"The number of graph objects passed in, {len(graphs)}, "
                    f"must match the number of edge types, {len(edge_types)}."
                )
            if any(not isinstance(graph, (nx.Graph, nx.DiGraph)) for graph in graphs):
                raise RuntimeError(
                    "All graph object inputs must be one of Networkx Graph or DiGraph."
                )
            nodes = set(graphs[0].nodes)

            # dictionary of internal graphs
            self._edge_graphs = {
                edge_type: graph for edge_type, graph in zip(edge_types, graphs)
            }
        else:
            nodes = []
            self._edge_graphs = dict()

        self.node_dict_factory = self.node_dict_factory
        self.node_attr_dict_factory = self.node_attr_dict_factory
        self._node = self.node_dict_factory()  # empty node attribute dict
        # ensure nodes are all within the necessary data structures
        self.add_nodes_from(nodes)

        # dictionary for graph attributes
        self.graph_attr_dict_factory = self.graph_attr_dict_factory
        self.graph = self.graph_attr_dict_factory()
        # load graph attributes (must be after convert)
        self.graph.update(attr)

    def __str__(self):
        """Returns a short summary of the graph.

        Graph information including the graph name (if any), graph type, and the
        number of nodes and edges.

        Examples
        --------
        >>> G = pywhy_nx.MixedEdgeGraph(name="foo")
        >>> str(G)
        "MixedEdgeGraph named 'foo' with 0 nodes and 0 edges and 0 edge types"
        """
        return "".join(
            [
                type(self).__name__,
                f" named {self.name!r}" if self.name else "",
                f" with {self.number_of_nodes()} nodes and {self.number_of_edges()} edges",
                f" and {self.number_of_edge_types()} edge types",
            ]
        )

    def number_of_edge_types(self):
        """The number of edge types."""
        return len(self.edge_types)

    @property
    def name(self):
        """String identifier of the graph.

        This graph attribute appears in the attribute dict G.graph
        keyed by the string ``"name"``. as well as an attribute (technically
        a property) ``G.name``. This is entirely user controlled.
        """
        return self.graph.get("name", "")

    @name.setter
    def name(self, s):
        self.graph["name"] = s

    @property
    def edge_types(self):
        return list(self._edge_graphs.keys())

    def get_graphs(self, edge_type="all"):
        """Get graphs representing the mixed-edges.

        Parameters
        ----------
        edge_type : str, optional
            The graph of the edge type to return, by default 'all', which
            will then return a dictionary of all edge graphs keyed by their
            edge type string.

        Returns
        -------
        graph : Graph | dictionary of Graph
            The graph representing a specific type of edge, or all edges.
        """
        if edge_type not in self._edge_graphs and edge_type != "all":
            raise ValueError(
                f"Querying the edge_type of a MixedEdgeGraph must be "
                f'"all", or one of {self.edge_types}, not {edge_type}.'
            )
        if edge_type == "all":
            return self._edge_graphs
        else:
            return self._edge_graphs[edge_type]

    @cached_property
    def nodes(self):
        # simply return the NodeView of the first graph
        return NodeView(self)

    def _apply_to_all_graphs(self, func_str, *args, **kwargs):
        """Utility for applying a common function to all internal graphs."""
        return_vals = []
        for graph in self._edge_graphs.values():
            graph_func = getattr(graph, func_str)
            try:
                return_val = graph_func(*args, **kwargs)
                return_vals.append(return_val)
            except NetworkXError as e:
                if KeyError == e.__cause__:
                    raise NetworkXError(e)
        return return_vals

    def _get_internal_graph(self, edge_type):
        if edge_type not in self.edge_types:
            raise ValueError(
                f"Edge type {edge_type} not part of the "
                f"existing edge types in graph."
            )
        return self._edge_graphs[edge_type]

    def _internal_graph_nx_type(self, edge_type):
        if edge_type not in self.edge_types:
            raise ValueError(
                f"Edge type {edge_type} not part of the "
                f"existing edge types in graph."
            )
        nx_graph_func = type(self._edge_graphs[edge_type])
        return nx_graph_func

    def add_node(self, node_for_adding, **attr):
        if node_for_adding not in self._node:
            if node_for_adding is None:
                raise ValueError("None cannot be a node")
            attr_dict = self._node[node_for_adding] = self.node_attr_dict_factory()
            attr_dict.update(attr)
        else:  # update attr even if node already exists
            self._node[node_for_adding].update(attr)
        self._apply_to_all_graphs("add_node", node_for_adding, **attr)

    def add_nodes_from(self, nodes_for_adding, **attr):
        for n in nodes_for_adding:
            try:
                newnode = n not in self._node
                newdict = attr
            except TypeError:
                n, ndict = n
                newnode = n not in self._node
                newdict = attr.copy()
                newdict.update(ndict)
            if newnode:
                if n is None:
                    raise ValueError("None cannot be a node")
                self._node[n] = self.node_attr_dict_factory()
            self._node[n].update(newdict)
            self._apply_to_all_graphs("add_node", n, **attr)

    def remove_node(self, n):
        try:
            del self._node[n]
        except KeyError as err:  # NetworkXError if n not in self
            raise NetworkXError(f"The node {n} is not in the graph.") from err
        self._apply_to_all_graphs("remove_node", n)

    def remove_nodes_from(self, nodes):
        for n in nodes:
            try:
                del self._node[n]
            except KeyError:
                pass
        self._apply_to_all_graphs("remove_nodes_from", nodes)

    def has_node(self, n):
        """Returns True if the graph contains the node n.

        Identical to ``n in G``

        Parameters
        ----------
        n : node
            The node to query. Identical to ``n in G``.

        Returns
        -------
        has : bool
            Whether or not the graph has node 'n'.
        """
        try:
            return n in self._node
        except TypeError:
            return False

    def number_of_nodes(self):
        """Returns the number of nodes in the graph.

        See Also
        --------
        order: identical method
        __len__: identical method
        """
        return len(self.nodes)

    def order(self):
        """Returns the number of nodes in the graph.

        See Also
        --------
        number_of_nodes: identical method
        __len__: identical method
        """
        return len(self.nodes)

    def clear(self):
        self._apply_to_all_graphs("clear")
        self._node.clear()
        self.graph.clear()

    def clear_edges(self, edge_type="all"):
        if edge_type == "all":
            self._apply_to_all_graphs("clear_edges")
        else:
            if edge_type not in self.edge_types:
                raise ValueError(f"edge_type, {edge_type} is not present in the graph.")
            self._get_internal_graph(edge_type=edge_type).clear_edges()

    def clear_edge_types(self):
        """Clear all edge types from graph."""
        self._edge_graphs.clear()

    def __iter__(self):
        """Iterate over the nodes. Use: 'for n in G'.

        An iterator over all nodes in the graph.
        """
        return iter(self.nodes)

    def __contains__(self, n):
        """Returns True if n is a node, False otherwise. Use: 'n in G'."""
        try:
            return n in self.nodes
        except TypeError:
            return False

    def __len__(self):
        """Returns the number of nodes in the graph. Use: 'len(G)'.

        See Also
        --------
        number_of_nodes: identical method
        order: identical method
        """
        return len(self._node)

    def __getitem__(self, n):
        """Returns a dict of neighbors of node n.  Use: 'G[n]'.

        The adjacency dictionary for nodes connected to n.

        Notes
        -----
        G[n] is the same as G.adj[n] and similar to G.neighbors(n)
        (which is an iterator over G.adj[n])
        """
        return self.adj[n]

    def has_edge(self, u, v, edge_type="any"):
        """Returns True if the edge (u, v) is in the graph.

        This is the same as ``v in G[u]`` without KeyError exceptions.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        edge_type : str
            Specifies a specific edge type. If 'any' (default), then
            will check if any edge exists between ``u`` and ``v`` across
            all edge types.

        Returns
        -------
        edge_ind : bool
            True if edge is in the graph, False otherwise.
        """
        if edge_type == "any":
            return any(self._apply_to_all_graphs("has_edge", u, v))
        else:
            return self._get_internal_graph(edge_type=edge_type).has_edge(u, v)

    def add_edge(self, u_of_edge, v_of_edge, edge_type="all", **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary.

        Parameters
        ----------
        u_for_edge, v_for_edge : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        edge_type : str
            The edge type. By default 'all', which
            will then add an edge in all edge type subgraphs.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges
        """
        u, v = u_of_edge, v_of_edge
        # add nodes
        if u not in self._node:
            self.add_node(u)
        if v not in self._node:
            self.add_node(v)
        if edge_type == "all":
            self._apply_to_all_graphs("add_edge", u_of_edge, v_of_edge, **attr)
        else:
            self._get_internal_graph(edge_type).add_edge(u_of_edge, v_of_edge, **attr)

    def add_edges_from(self, ebunch_to_add, edge_type, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as 2-tuples (u, v) or
            3-tuples (u, v, d) where d is a dictionary containing edge data.
        edge_type : str
            The edge type to add edges to. By default 'all', which
            will then add an edge in all edge type subgraphs.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Edge attributes specified in an ebunch take precedence over
        attributes specified via keyword arguments.
        """
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, _ = e
            elif ne == 2:
                u, v = e
            else:
                raise NetworkXError(f"Edge tuple {e} must be a 2-tuple or 3-tuple.")
            if u not in self._node:
                if u is None:
                    raise ValueError("None cannot be a node")
                self.add_node(u, **attr)
            if v not in self._node:
                if v is None:
                    raise ValueError("None cannot be a node")
                self.add_node(v, **attr)

        if edge_type == "all":
            edge_type = self.edge_types
        else:
            edge_type = [edge_type]

        for _edge_type in edge_type:
            self._get_internal_graph(_edge_type).add_edges_from(ebunch_to_add, **attr)

    def remove_edge(self, u, v, edge_type="all"):
        """Remove an edge between u and v.

        Parameters
        ----------
        u, v : nodes
            Remove an edge between nodes u and v.
        edge_type : str
            The edge type. By default 'all', which
            will then remove the edge in all edge type subgraphs (if it exists).

        Raises
        ------
        NetworkXError
            If there is not an edge between u and v, or
            if there is no edge with the specified key.

        See Also
        --------
        remove_edges_from : remove a collection of edges
        """
        if edge_type == "all":
            self._apply_to_all_graphs("remove_edge", u, v)
        else:
            self._get_internal_graph(edge_type).remove_edge(u, v)

    def remove_edges_from(self, ebunch, edge_type="all"):
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
        """
        if edge_type == "all":
            self._apply_to_all_graphs("remove_edges_from", ebunch)
        else:
            self._get_internal_graph(edge_type).remove_edges_from(ebunch)

    def copy(self):
        """Returns a copy of the graph.

        The copy method by default returns an independent shallow copy
        of the graph and attributes. That is, if an attribute is a
        container, that container is shared by the original an the copy.
        Use Python's `copy.deepcopy` for new containers.

        Notes
        -----
        All copies reproduce the graph structure, but data attributes
        may be handled in different ways. There are four types of copies
        of a graph that people might want. See :meth:`networkx.Graph.copy`
        for doc string.

        Parameters
        ----------
        as_view : bool, optional (default=False)
            If True, the returned graph-view provides a read-only view
            of the original graph without actually copying any data.

        Returns
        -------
        G : Graph
            A copy of the graph.

        See Also
        --------
        to_directed: return a directed copy of the graph.
        networkx.Graph.copy: for full copy docstring.
        """
        G = self.__class__()
        G.graph.update(self.graph)

        # add all internal graphs to the copy
        int_graph_copies = []
        for edge_type in self.edge_types:
            graph_func = self._internal_graph_nx_type(edge_type=edge_type)
            int_graph_copies.append(graph_func())

            if edge_type not in G.edge_types:
                G.add_edge_type(graph_func(), edge_type)

        # add all nodes and edges now
        G.add_nodes_from((n, d.copy()) for n, d in self.nodes.items())
        for edge_type, adj in self.adj.items():
            for u, nbrs in adj.items():
                for v, datadict in nbrs.items():
                    G.add_edge(u, v, edge_type, **datadict.copy())
        return G

    def is_multigraph(self):
        """Returns True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Returns True if graph is directed, False otherwise."""
        return False
        # # TODO: need to double check that any directed graph algos. work as exp.
        # return any([isinstance(graph, nx.DiGraph) for graph in self.get_graphs()])

    def is_mixed(self):
        return True

    def add_edge_type(self, graph, edge_type):
        if edge_type in self._edge_graphs:
            raise ValueError(f"edge_type {edge_type} is already in the graph.")
        if not isinstance(graph, (nx.Graph, nx.DiGraph)):
            raise RuntimeError(
                f"{graph} must be an instantiated instance of a base networkx "
                f"graph [nx.Graph, nx.DiGraph]"
            )

        # ensure new graph type has all nodes
        self._edge_graphs[edge_type] = graph

        # if we have nodes already, or if we have an empty edge-type subgraph
        if self._node or self.edge_types:
            graph.add_nodes_from(self._node)
            self.add_nodes_from(graph.nodes)

    def add_edge_types_from(self, graphs, edge_types):
        if len(graphs) != len(edge_types):
            raise ValueError("Number of graphs and edge types must be the same.")
        for edge_type, graph in zip(edge_types, graphs):
            self.add_edge_type(graph, edge_type)

    def remove_edge_type(self, edge_type):
        self._edge_graphs.pop(edge_type)

    def to_undirected(self):
        """Returns an undirected representation of the digraph.

        Returns
        -------
        G : Graph
            An undirected graph with the same name and nodes and
            with edge (u, v, data) if either (u, v, data) or (v, u, data)
            is in the digraph.  If both edges exist in a sub digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

        Notes
        -----
        This returns a "deepcopy" of the edge, node, and
        graph attributes which attempts to completely copy
        all of the data and references.

        This is in contrast to the similar D=MultiDiGraph(G) which
        returns a shallow copy of the data.

        See the Python copy module for more information on shallow
        and deep copies, https://docs.python.org/3/library/copy.html.

        Warning: If you have subclassed MultiDiGraph to use dict-like
        objects in the data structure, those changes do not transfer
        to the MultiGraph created by this method.
        """
        graph_class = nx.Graph

        # deepcopy when not a view
        G = graph_class()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self.nodes.items())
        G.add_edges_from(
            (u, v, deepcopy(d))
            for _, edge_adj in self.adj.items()
            for u, nbrs in edge_adj.items()
            for v, d in nbrs.items()
        )
        return G

    def to_directed(self):
        """Returns a directed representation of the graph.

        Returns
        -------
        G : DiGraph
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
        and deep copies, https://docs.python.org/3/library/copy.html.

        Warning: If you have subclassed Graph to use dict-like objects
        in the data structure, those changes do not transfer to the
        DiGraph created by this method.
        """
        graph_class = nx.DiGraph

        # deepcopy when not a view
        G = graph_class()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from(
            (u, v, deepcopy(d))
            for _, edge_adj in self.adj.items()
            for u, nbrs in edge_adj.items()
            for v, d in nbrs.items()
        )
        return G

    def number_of_edges(self, u=None, v=None, edge_type="all"):
        """Returns the number of edges between two nodes.

        Parameters
        ----------
        u, v : nodes, optional (default=all edges)
            If u and v are specified, return the number of edges between
            u and v. Otherwise return the total number of all edges.
        edge_type : str, optional
            The edge type to query for number of edges. If 'all' (default)
            will count the number of edges regardless of edge type.

        Returns
        -------
        nedges : int
            The number of edges in the graph.  If nodes ``u`` and ``v`` are
            specified return the number of edges between those nodes. If
            the graph is directed, this only returns the number of edges
            from ``u`` to ``v``.

        See Also
        --------
        size
        """
        if edge_type != "all":
            return self._get_internal_graph(edge_type).number_of_edges(u=u, v=v)

        n_edges = sum(self._apply_to_all_graphs("number_of_edges", u, v))
        return n_edges

    def nbunch_iter(self, nbunch=None):
        """Returns an iterator over nodes contained in nbunch that are
        also in the graph.

        The nodes in nbunch are checked for membership in the graph
        and if not are silently ignored.

        Parameters
        ----------
        nbunch : single node, container, or all nodes (default= all nodes)
            The view will only report edges incident to these nodes.

        Returns
        -------
        niter : iterator
            An iterator over nodes in nbunch that are also in the graph.
            If nbunch is None, iterate over all nodes in the graph.

        Raises
        ------
        NetworkXError
            If nbunch is not a node or sequence of nodes.
            If a node in nbunch is not hashable.
        """
        if self.edge_types:
            edge_type = self.edge_types[0]
        else:
            raise NetworkXError("No edge types inside graph")
        return self._get_internal_graph(edge_type=edge_type).nbunch_iter(nbunch=nbunch)

    # TODO: For below make sure certain checks are made to ensure api vs networkx is the same
    def update(self, edges=None, nodes=None, edge_type=None):
        """Update the graph using nodes/edges/graphs as input.

        Like dict.update, this method takes a graph as input, adding the
        graph's nodes and edges to this graph. It can also take two inputs:
        edges and nodes. Finally it can take either edges or nodes.
        To specify only nodes the keyword ``nodes`` must be used.

        The collections of edges and nodes are treated similarly to
        the add_edges_from/add_nodes_from methods. When iterated, they
        should yield 2-tuples (u, v) or 3-tuples (u, v, datadict).

        Parameters
        ----------
        edges : nx.Graph object, collection of edges, or None
            The first parameter can be a graph or some edges. If it has
            attributes ``nodes`` and `edges`, then it is taken to be a
            Graph-like object and those attributes are used as collections
            of nodes and edges to be added to the graph.
            If the first parameter does not have those attributes, it is
            treated as a collection of edges and added to the graph.
            If the first argument is None, no edges are added.
        nodes : collection of nodes, or None
            The second parameter is treated as a collection of nodes
            to be added to the graph unless it is None.
            If ``edges is None`` and ``nodes is None`` an exception is raised.
            If the first parameter is a Graph, then ``nodes`` is ignored.
        """
        if edges is not None:
            if edge_type is None and not isinstance(edges, MixedEdgeGraph):
                raise RuntimeError("Edge type is undefined.")
            if isinstance(edges, MixedEdgeGraph):
                raise RuntimeError("Not supported for updating with a graph yet.")

            if nodes is not None:
                self.add_nodes_from(nodes)
                self.add_edges_from(edges, edge_type=edge_type)
            else:
                # check if edges is a Graph object
                try:
                    graph_nodes = edges.nodes
                    graph_edges = edges.edges
                except AttributeError:
                    # edge not Graph-like
                    self.add_edges_from(edges, edge_type=edge_type)
                else:  # edges is Graph-like
                    self.add_nodes_from(graph_nodes.data())
                    self.add_edges_from(
                        graph_edges[edge_type].data(), edge_type=edge_type
                    )
                    self.graph.update(edges.graph)
        elif nodes is not None:
            # TODO: if nodes is supported internally for MixeedEdgeGraph, we don't need this check
            if len(self._edge_graphs) == 0:
                raise RuntimeError("No edge types defined yet.")
            self.add_nodes_from(nodes)
        else:
            raise NetworkXError("update needs nodes or edges input")

    @cached_property
    def adj(self):
        """Dictionary of graph adjacency objects holding the neighbors of each node.

        Each edge type has an adjacency object associated with it. For more information
        on the adjacency object itself, see the documentation in `networkx.Graph.adj`.

        Iterating over G.adj behaves like a dict. Useful idioms include the following
        for loop.

        >>> for edge_type, adj in G.adj.items():
        >>>     for nbr, datadict in adj[n].items():
        >>>          ...

        The main difference from non-mixed edge graph types is that ``adj`` here
        returns a dictionary of adjacency views, so neighbors can be queried within
        each edge type.

        Returns
        -------
        adj : dictionary of AdjacencyView
            A dictionary of edge types and their corresponding adjacency view objects.
        """
        return {edge_type: graph.adj for edge_type, graph in self._edge_graphs.items()}

    def edges(self, nbunch=None, data=False, default=None):
        """A dictionary of EdgeViews of the Graph as G.edges or G.edges().

        Each edge type has an EdgeView object associated with it. For more information
        on the EdgeView object itself, see the documentation in ``networkx.Graph.edges``.

        Parameters
        ----------
        nbunch : single node, container, or all nodes (default= all nodes)
            The view will only report edges from these nodes.
        data : string or bool, optional (default=False)
            The edge attribute returned in 3-tuple (u, v, ddict[data]).
            If True, return edge attribute dict in 3-tuple (u, v, ddict).
            If False, return 2-tuple (u, v).
        default : value, optional (default=None)
            Value used for edges that don't have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        edges : dictionary of EdgeView
            A dictionary of EdgeViews.

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.
        """
        return {
            edge_type_: graph.edges(nbunch=nbunch, data=data, default=default)
            for edge_type_, graph in self._edge_graphs.items()
        }

    def neighbors(self, n):
        nbrs = set()
        for _, G in self.get_graphs().items():
            nbrs = nbrs.union(set(nx.all_neighbors(G, n)))
        return iter(nbrs)

    def subgraph(self, nodes):
        """Returns a SubGraph view of the subgraph induced on ``nodes``.

        TODO: this does not work as expected with subclasses
        The induced subgraph of the graph contains the nodes in ``nodes``
        and the edges between those nodes.

        Parameters
        ----------
        nodes : list, iterable
            A container of nodes which will be iterated through once.

        Returns
        -------
        G : MixedEdgeGraph
            A copy of the graph with only the nodes.
        """
        # initialize list of empty internal graphs
        graph_classes = [
            self._internal_graph_nx_type(edge_type)() for edge_type in self.edge_types
        ]
        graph = self.__class__(**self.graph).copy()
        for edge_type, _graph in zip(self.edge_types, graph_classes):
            if edge_type not in graph.edge_types:
                graph.add_edge_type(_graph, edge_type)
        graph.add_nodes_from(nodes)

        # now add the edges for each edge type
        for edge_type, _graph in graph._edge_graphs.items():
            for node in nodes:
                edges = self._get_internal_graph(edge_type).edges(node)

                # only add edges from the induced subgraph
                for u, v in edges:
                    if u in set(nodes) and v in nodes:
                        _graph.add_edge(u, v)
        return graph

    def degree(self, nbunch=None, weight=None):
        """A DegreeView for the Graph as G.degree or G.degree().

        Parameters
        ----------
        nbunch : single node, container, or all nodes (default= all nodes)
            The view will only report edges incident to these nodes.

        weight : string or None, optional (default=None)
           The name of an edge attribute that holds the numerical value used
           as a weight.  If None, then each edge has weight 1.
           The degree is the sum of the edge weights adjacent to the node.

        Returns
        -------
        deg_dicts : dictionary of DegreeView | int
            If multiple nodes are requested (the default), returns a ``DegreeView``
            mapping nodes to their degree.
            If a single node is requested, returns the degree of the node as an integer.
        """
        # get the DegreeView for each internal graph
        deg_dicts = dict()
        for _edge_type in self.edge_types:
            deg_view = self._get_internal_graph(_edge_type).degree(
                nbunch=nbunch, weight=weight
            )
            deg_dicts[_edge_type] = deg_view
        return deg_dicts

    def size(self, weight=None, edge_type="all"):
        """Returns the number of edges or total of all edge weights.

        Parameters
        ----------
        weight : string or None, optional (default=None)
            The edge attribute that holds the numerical value used
            as a weight. If None, then each edge has weight 1.

        Returns
        -------
        size : float
            The number of edges or
            (if weight keyword is provided) the total weight sum.
            If weight is None, returns an int. Otherwise a float
            (or more general numeric if the weights are more general).

        See Also
        --------
        number_of_edges
        """
        if edge_type == "all":
            edge_types = self.edge_types

        s = 0
        for _edge_type in edge_types:
            s = sum(d for v, d in self.degree(weight=weight)[_edge_type])
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2

    def get_edge_data(self, u, v, default=None):
        """Returns the attribute dictionary associated with edge (u, v).

        This is identical to ``G[u][v]`` except the default is returned
        instead of an exception if the edge doesn't exist.

        Parameters
        ----------
        u, v : nodes
        default:  any Python object (default=None)
            Value to return if the edge (u, v) is not found.

        Returns
        -------
        edge_dict : dictionary
            The edge attribute dictionary.
        """
        edge_dict = dict()
        for edge_type_, graph in self.get_graphs().items():
            edge_data = graph.get_edge_data(u, v, default=default)
            if edge_data != default:
                edge_data = edge_data.get(edge_type_, dict())
            edge_dict[edge_type_] = edge_data
        return edge_dict
