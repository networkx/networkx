"""
Graph summarization finds smaller representations of graphs resulting in faster
runtime of algorithms, reduced storage needs, and noise reduction.
Summarization has applications in areas such as visualization, pattern mining,
clustering and community detection, and more.  Core graph summarization
techniques are grouping/aggregation, bit-compression,
simplification/sparsification, and influence based. Graph summarization
algorithms often produce either summary graphs in the form of supergraphs or
sparsified graphs, or a list of independent structures. Supergraphs are the
most common product, which consist of supernodes and original nodes and are
connected by edges and superedges, which represent aggregate edges between
nodes and supernodes.

Grouping/aggregation based techniques compress graphs by representing
close/connected nodes and edges in a graph by a single node/edge in a
supergraph. Nodes can be grouped together into supernodes based on their
structural similarities or proximity within a graph to reduce the total number
of nodes in a graph. Edge-grouping techniques group edges into lossy/lossless
nodes called compressor or virtual nodes to reduce the total number of edges in
a graph. Edge-grouping techniques can be lossless, meaning that they can be
used to re-create the original graph, or techniques can be lossy, requiring
less space to store the summary graph, but at the expense of lower
recontruction accuracy of the original graph.

Bit-compression techniques minimize the amount of information needed to
describe the original graph, while revealing structural patterns in the
original graph.  The two-part minimum description length (MDL) is often used to
represent the model and the original graph in terms of the model.  A key
difference between graph compression and graph summarization is that graph
summarization focuses on finding structural patterns within the original graph,
whereas graph compression focuses on compressions the original graph to be as
small as possible.  **NOTE**: Some bit-compression methods exist solely to
compress a graph without creating a summary graph or finding comprehensible
structural patterns.

Simplification/Sparsification techniques attempt to create a sparse
representation of a graph by removing unimportant nodes and edges from the
graph.  Sparsified graphs differ from supergraphs created by
grouping/aggregation by only containing a subset of the original nodes and
edges of the original graph.

Influence based techniques aim to find a high-level description of influence
propagation in a large graph.  These methods are scarce and have been mostly
applied to social graphs.

*dedensification* is a grouping/aggregation based technique to compress the
neighborhoods around high-degree nodes in unweighted graphs by adding
compressor nodes that summarize multiple edges of the same type to
high-degree nodes (nodes with a degree greater than a given threshold).
Dedensification was developed for the purpose of increasing performance of
query processing around high-degree nodes in graph databases and enables direct
operations on the compressed graph.  The structural patterns surrounding
high-degree nodes in the original is preserved while using fewer edges and
adding a small number of compressor nodes.  The degree of nodes present in the
original graph is also preserved. The current implementation of dedensification
supports graphs with one edge type.

For more information on graph summarization, see `Graph Summarization Methods
and Applications: A Survey <https://dl.acm.org/doi/abs/10.1145/3186727>`_
"""
import networkx as nx
import logging


logger = logging.getLogger(__name__)


__all__ = ["dedensify", "SNAP"]


def dedensify(G, threshold, prefix=None, copy=True):
    """Compresses neighborhoods around high-degree nodes

    Reduces the number of edges to high-degree nodes by adding compressor nodes
    that summarize multiple edges of the same type to high-degree nodes (nodes
    with a degree greater than a given threshold).  Dedensification also has
    the added benefit of reducing the number of edges around high-degree nodes.
    The implementation currently supports graphs with a single edge type.

    Parameters
    ----------
    G: graph
       A networkx graph
    threshold: int
       Minimum degree threshold of a node to be considered a high degree node.
       The threshold must be greater than or equal to 2.
    prefix: str or None, optional (default: None)
       An optional prefix for denoting compressor nodes
    copy: bool, optional (default: True)
       Indicates if dedensification should be done inplace

    Returns
    -------
    dedensified networkx graph : (graph, set)
        2-tuple of the dedensified graph and set of compressor nodes

    Notes
    -----
    According to the algorithm in [1]_, removes edges in a graph by
    compressing/decompressing the neighborhoods around high degree nodes by
    adding compressor nodes that summarize multiple edges of the same type
    to high-degree nodes.  Dedensification will only add a compressor node when
    doing so will reduce the total number of edges in the given graph. This
    implementation currently supports graphs with a single edge type.

    Examples
    --------
    Dedensification will only add compressor nodes when doing so would result
    in fewer edges::

        >>> original_graph = nx.DiGraph()
        >>> original_graph.add_nodes_from(
        ...     ["1", "2", "3", "4", "5", "6", "A", "B", "C"]
        ... )
        >>> original_graph.add_edges_from(
        ...     [
        ...         ("1", "C"), ("1", "B"),
        ...         ("2", "C"), ("2", "B"), ("2", "A"),
        ...         ("3", "B"), ("3", "A"), ("3", "6"),
        ...         ("4", "C"), ("4", "B"), ("4", "A"),
        ...         ("5", "B"), ("5", "A"),
        ...         ("6", "5"),
        ...         ("A", "6")
        ...     ]
        ... )
        >>> c_graph, c_nodes = nx.dedensify(original_graph, threshold=2)
        >>> original_graph.number_of_edges()
        15
        >>> c_graph.number_of_edges()
        14

    A dedensified, directed graph can be "densified" to reconstruct the
    original graph::

        >>> original_graph = nx.DiGraph()
        >>> original_graph.add_nodes_from(
        ...     ["1", "2", "3", "4", "5", "6", "A", "B", "C"]
        ... )
        >>> original_graph.add_edges_from(
        ...     [
        ...         ("1", "C"), ("1", "B"),
        ...         ("2", "C"), ("2", "B"), ("2", "A"),
        ...         ("3", "B"), ("3", "A"), ("3", "6"),
        ...         ("4", "C"), ("4", "B"), ("4", "A"),
        ...         ("5", "B"), ("5", "A"),
        ...         ("6", "5"),
        ...         ("A", "6")
        ...     ]
        ... )
        >>> c_graph, c_nodes = nx.dedensify(original_graph, threshold=2)
        >>> # re-densifies the compressed graph into the original graph
        >>> for c_node in c_nodes:
        ...     all_neighbors = set(nx.all_neighbors(c_graph, c_node))
        ...     out_neighbors = set(c_graph.neighbors(c_node))
        ...     for out_neighbor in out_neighbors:
        ...         c_graph.remove_edge(c_node, out_neighbor)
        ...     in_neighbors = all_neighbors - out_neighbors
        ...     for in_neighbor in in_neighbors:
        ...         c_graph.remove_edge(in_neighbor, c_node)
        ...         for out_neighbor in out_neighbors:
        ...             c_graph.add_edge(in_neighbor, out_neighbor)
        ...     c_graph.remove_node(c_node)
        ...
        >>> nx.is_isomorphic(original_graph, c_graph)
        True

    References
    ----------
    .. [1] Maccioni, A., & Abadi, D. J. (2016, August).
       Scalable pattern matching over compressed graphs via dedensification.
       In Proceedings of the 22nd ACM SIGKDD International Conference on
       Knowledge Discovery and Data Mining (pp. 1755-1764).
       http://www.cs.umd.edu/~abadi/papers/graph-dedense.pdf
    """
    if threshold < 2:
        raise nx.NetworkXError("The degree threshold must be >= 2")

    degrees = G.in_degree if G.is_directed() else G.degree
    # Group nodes based on degree threshold
    high_degree_nodes = set([n for n, d in degrees if d > threshold])
    low_degree_nodes = G.nodes() - high_degree_nodes

    auxillary = {}
    for node in G:
        high_degree_neighbors = frozenset(high_degree_nodes & set(G[node]))
        if high_degree_neighbors:
            if high_degree_neighbors in auxillary:
                auxillary[high_degree_neighbors].add(node)
            else:
                auxillary[high_degree_neighbors] = {node}

    if copy:
        G = G.copy()

    compressor_nodes = set()
    for index, (high_degree_nodes, low_degree_nodes) in enumerate(auxillary.items()):
        low_degree_node_count = len(low_degree_nodes)
        high_degree_node_count = len(high_degree_nodes)
        old_edges = high_degree_node_count * low_degree_node_count
        new_edges = high_degree_node_count + low_degree_node_count
        if old_edges <= new_edges:
            continue
        compression_node = "".join(str(node) for node in high_degree_nodes)
        if prefix:
            compression_node = str(prefix) + compression_node
        for node in low_degree_nodes:
            for high_node in high_degree_nodes:
                if G.has_edge(node, high_node):
                    G.remove_edge(node, high_node)

            G.add_edge(node, compression_node)
        for node in high_degree_nodes:
            G.add_edge(compression_node, node)
        compressor_nodes.add(compression_node)
    return G, compressor_nodes


class _GABitmap(object):
    """
    A base data structure for splitting/merging groups of nodes together based
    on node attributes and relationship (edges) types between groups.  In this
    implementation, relationship types are determined by the combinations of
    values from the given edge attributes.  For example, if two attributes,
    'size' ('small', 'medium', 'large') and 'color' ('yellow', 'blue', 'red'),
    are provided, provided, 9 potential relationship types will be used:

    1. ('small', 'yellow')
    2. ('small', 'blue')
    3. ('small', 'red')
    4. ('medium', 'yellow'),
    5. ('medium', 'blue')
    6. ('medium', 'red')
    7. ('large', 'yellow')
    8. ('large', 'blue')
    9. ('large', 'red')

    Attributes
    ----------
    node_attributes: tuple
        node attributes being grouped
    group_ids: list<int>
        IDs corresponding to the current groups.
    group_sets: list<set<int>>
        Node IDs corresponding to membership in a group ID.
    """

    __slots__ = ("node_attributes", "group_sets", "group_ids")

    def __init__(self, node_attributes, group_sets, **kwargs):
        self.node_attributes = node_attributes
        self.group_sets = group_sets
        group_count = len(group_sets)
        self.group_ids = list(range(group_count))

    def __repr__(self):
        group_count = len(self.group_ids)
        return "<%s %s groups=%i>" % (self.__class__.__name__, id(self), group_count)

    def __len__(self):
        return len(self.group_ids)

    def __getitem__(self, key):
        return self.group_sets[key].copy()

    def __iter__(self):
        for group_id in self.group_ids:
            yield group_id

    def summarize(self, G, *args, **kwargs):
        """
        Summarizes the given graph by grouping nodes by relationship attributes

        Parameters
        ----------
        G: graph
            Networkx Graph to be summarized

        Returns
        -------
        summarized graph and supernodes: (graph, dict)
            2-tuple of the summarized graphs and the supernodes
        """
        raise NotImplementedError("The summarize method has not been implemented")

    @staticmethod
    def _update_groups(
        group_ids,
        group_sets,
        relationship_attributes,
        old_group_id,
        new_groups,
        group_lookup,
    ):
        """
        Parameters
        ----------
        group_ids: iterable
            Group ids of the current graph summary
        group_sets: iterable
            Group membership of nodes
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization
        old_group_id: int
            the ID of the group that was last split
        new_groups: iterable
            List of sets of new groups of nodes
        group_lookup: dict
            Dictionary containing the group assignment of each node in the graph

        Returns
        -------
        2-tuple:
            updated group_ids
            updated_group_sets
        """
        old_group_count = len(group_ids)
        new_group_count = len(new_groups)

        for new_group in new_groups:
            group_sets[old_group_id] -= new_group

        for new_group in new_groups:
            group_sets.append(new_group)

        new_total_group_count = old_group_count + new_group_count
        updated_groups = set([old_group_id]) | set(
            range(old_group_count, new_total_group_count)
        )
        for group_id in updated_groups:
            for node in group_sets[group_id]:
                group_lookup[node] = group_id

        group_ids = list(range(new_total_group_count))
        return group_ids, group_sets

    def _build_graph(
        self,
        G,
        group_ids,
        group_sets,
        relationship_attributes,
        bitmap,
        participation_counts,
        prefix,
    ):
        """
        Parameters
        ----------
        G: networkx.Graph
            the original graph to be summarized
        group_ids: iterable
            Group ids of the current graph summary
        group_sets: iterable
            Group membership of nodes
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization
        bitmap: dict
            A data structure indicating the relationships nodes have to other groups by relationship type
        participation_counts: dict
            A data structure indicating the number of members in a group have edges connecting them to
        old_group_id: int
            the ID of the group that was last split
        new_groups: iterable
            List of sets of new groups of nodes
        group_lookup: dict
            Group assignments of each node in the graph

        Returns
        -------
        2-tuple (graph, dict):
            summary graph: Networkx graph
            supernodes: node-set pairings of supernodes and associated nodes
        """
        output = G.copy()
        output.clear()
        node_label_lookup = dict()
        supernode_lookup = dict()
        for group_id in group_ids:
            group_set = group_sets[group_id]
            if len(group_set) > 1:
                node = "%s%s" % (prefix, group_id)
            else:
                (node,) = group_set
            original_node = next(iter(group_set))
            node_attributes = dict()
            for attribute in self.node_attributes:
                attribute_value = G.nodes[original_node][attribute]
                node_attributes[attribute] = attribute_value
            output.add_node(node, **node_attributes)
            node_label_lookup[group_id] = node
            supernode_lookup[node] = group_set

        for group_id in group_ids:
            group_set = group_sets[group_id]
            node = next(iter(group_set))
            for other_group_id, grouping in enumerate(bitmap[node]):
                for relationship_index, relationship in enumerate(grouping):
                    if relationship:
                        neighbor_group = group_sets[other_group_id]
                        neighbor = next(iter(neighbor_group))
                        edge = (node, neighbor)
                        relationship_values = self._relationship_key(
                            G, edge, relationship_attributes
                        )
                        if relationship_values:
                            edge_attributes = dict(
                                **zip(relationship_attributes, relationship_values)
                            )
                        else:
                            edge_attributes = dict()
                        summary_source_node = node_label_lookup[group_id]
                        summary_target_node = node_label_lookup[other_group_id]
                        summary_graph_edge = (summary_source_node, summary_target_node)
                        output.add_edge(*summary_graph_edge, **edge_attributes)

        return output, supernode_lookup

    @classmethod
    def _relationship_keys(cls, G, relationship_attributes):
        """
        Produces a set of all relationship types that can be found in graph G

        Parameters
        ----------
        G: graph
            A Networkx graph
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization

        Returns
        -------
        set: The relationship types found in graph G
        """
        relationship_values = set()
        for edge in G.edges():
            relationship_value = cls._relationship_key(G, edge, relationship_attributes)
            relationship_values.add(relationship_value)
        return relationship_values

    @staticmethod
    def _relationship_key(G, edge, relationship_attributes):
        """
        Produces an immutable representation of the specified edge.  This
        object is used as a unique identifier for each respective edge type in
        graph G.

        Parameters
        ----------
        G: graph
            A Networkx graph
        edge: tuple
            A tuple of the source,& target nodes in the graph
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization

        Returns
        -------
        tuple: A representation of the specified edge based on the attribute
            values
        """
        if relationship_attributes:
            relationship_value = []
            edge_data = G.get_edge_data(*edge)
            for attribute in relationship_attributes:
                attribute_value = edge_data.get(attribute)
                relationship_value.append(attribute_value)
            relationship_value = tuple(relationship_value)
        else:
            relationship_value = None
        return relationship_value

    @classmethod
    def _calculate_bitmap(
        cls,
        G,
        group_ids,
        group_sets,
        relationship_attributes,
        relationship_index_lookup,
        group_lookup=None,
    ):
        """
        Produces a data structure indicating if a given node in the original
        graph has one or more edges to nodes in another given group

        Parameters
        ----------
        G: graph
            A Networkx graph
        group_ids: iterable
            Group ids of the current graph summary
        group_sets: iterable
            Group membership of nodes
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization
        relationship_index_lookup: dict
            A relationship key mapping the relationship edge values to it's
            index/ID
        group_lookup: dict
            dictionary of nodes and their current group ID
        """
        unique_relationship_count = len(relationship_index_lookup)

        if not group_lookup:
            group_lookup = dict()
            for node in G.nodes:
                for group_id, group_set in zip(group_ids, group_sets):
                    if node in group_set:
                        group_lookup[node] = group_id
                        break
        participation_counts = dict()
        bitmap = dict()
        for group_id in group_ids:
            group_nodes = group_sets[group_id]
            participation_counts[group_id] = [
                [0] * unique_relationship_count for _ in group_ids
            ]

            for node in group_nodes:
                bitmap[node] = [[False] * unique_relationship_count for _ in group_ids]
                neighbors = set(G.neighbors(node))
                neighbor_group_relationships = set()
                for neighbor in neighbors:
                    edge = (node, neighbor)
                    relationship_key = cls._relationship_key(
                        G, edge, relationship_attributes
                    )
                    relationship_index = relationship_index_lookup[relationship_key]

                    neighbor_group_id = group_lookup[neighbor]
                    neighbor_group_relationships.add(
                        (neighbor_group_id, relationship_index)
                    )
                    bitmap[node][neighbor_group_id][relationship_index] = True

                for (
                    neighbor_group_id,
                    relationship_index,
                ) in neighbor_group_relationships:
                    participation_counts[group_id][neighbor_group_id][
                        relationship_index
                    ] += 1

        return bitmap, participation_counts

    @staticmethod
    def _attribute_compatible_groups(G, node_attributes):
        """
        Produces a list of Attribute compatible (A-compatible) groupings.

        An A-compatible grouping is where each group of nodes each have all of the
        same values for each node attribute.

        Parameters
        ----------
        G: graph
            A Networkx graph
        node_attributes: iterable
            The node attributes that can be found in nodes in the graph, and are to be recognized in the
            summarization

        Returns
        -------
        list: A list of group of nodes, grouped by their collective attribute values
        """
        raw_groups = dict()
        for node in G.nodes():
            node_data = []
            for attribute in node_attributes:
                attribute_value = G.nodes[node][attribute]
                node_data.append(attribute_value)
            node_key = tuple(node_data)
            raw_groups.setdefault(node_key, set())
            raw_groups[node_key].add(node)

        return list(raw_groups.values())

    @classmethod
    def from_graph(cls, G, node_attributes):
        """
        Parameters
        ----------
        G: graph
            A Networkx graph
        node_attributes: iterable
            list of node attributes to use to group nodes

        Returns
        -------
        _GABitmap:  A _GABitmap instance of the A-compatible node groupings
        """
        group_sets = cls._attribute_compatible_groups(G, node_attributes)
        return cls(node_attributes, group_sets)


class SNAP(_GABitmap):
    """
    A data structure for splitting/merging groups of nodes together based on
    shared relationships between groups.  Currently supports categorical
    attributes, not continuous attributes.

    Implements the SNAP summarization algorithm as defined in [1]_,
    for producing Attribute-Relationship compatible (AR-compatible) groupings
    of nodes, where each node in each group has the same node attributes
    and edges of the same type with nodes in the same other groups.

    For more information see `Efficient Aggregation for Graph Summarization`
    <http://www1.se.cuhk.edu.hk/~seem5010/slides/sigmod2008_summarization.pdf>_

    Attributes
    ----------
    node_attributes: tuple
        node attributes being grouped
    group_ids: list<int>
        IDs corresponding to the current groups.
    group_sets: list<set<int>>
        Node IDs corresponding to membership in a group ID.

    References
    ----------
    .. [1] Y. Tian, R. A. Hankins, and J. M. Patel. Efficient aggregation
       for graph summarization. In Proc. 2008 ACM-SIGMOD Int. Conf.
       Management of Data (SIGMOD’08), pages 567–580, Vancouver, Canada,
       June 2008.
    """

    __slots__ = ("node_attributes", "group_sets", "group_ids")

    def summarize(self, G, relationship_attributes=None, prefix="Supernode-"):
        """
        Summarizes the given graph by grouping nodes by relationship attributes

        Parameters
        ----------
        G: graph
            Networkx Graph to be summarized
        relationship_attributes: iterable, optional
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization.  If provided, unique
            combinations of the attribute values found in the graph are used to
            determine the edge types in the graph.  If not provided, all edges
            are considered to be of the same type.
        prefix: str
            The prefix used to denote supernodes in the summary graph

        Returns
        -------
        tuple:
            networkx.Graph: summary graph
            dict: supernode keys and values are the nodes in those supernodes

        Examples
        --------
        >>> G = nx.karate_club_graph()
        >>> gamap = SNAP.from_graph(G, node_attributes=('club', ))
        >>> summary_graph, supernodes = gamap.summarize(G)

        Notes
        -----
        The summary graph produced is called a maximum Attribute-Relationship
        compatible (AR-compatible) grouping.  According to [1]_, an
        AR-compatible grouping means that all nodes in each group have the same
        exact node attribute values and the same exact relationships and
        relationship types to nodes in the same groups.  The maximal
        AR-compatible grouping is the grouping with the minimal cardinality.

        The AR-compatible grouping is the most detailed grouping provided by
        any of the *SNAP algorithms.

        References
        ----------
        .. [1] Y. Tian, R. A. Hankins, and J. M. Patel. Efficient aggregation
           for graph summarization. In Proc. 2008 ACM-SIGMOD Int. Conf.
           Management of Data (SIGMOD’08), pages 567–580, Vancouver, Canada,
           June 2008.
        """
        (
            group_ids,
            group_sets,
            participation_counts,
            bitmap,
            relationship_index_lookup,
        ) = self._build_data_structures(G, relationship_attributes)
        return self._build_graph(
            G,
            group_ids,
            group_sets,
            relationship_attributes,
            bitmap,
            participation_counts,
            prefix=prefix,
        )

    def _build_data_structures(self, G, relationship_attributes):
        """
        Finds the AR-compatible grouping of graph G and returns data structures
        to efficiently process those groupings.

        An Attribute-Relationship compatible (AR-compatible) grouping is where
        all nodes in each group have the same exact node attribute values and
        have the same exact relationship types to nodes in the same exact
        groups.

        Parameters
        ----------
        G: graph
            Networkx Graph to be summarized
        relationship_attributes: iterable
            The edge attributes that can be found in edges in the graph, and
            are to be recognized in the summarization

        Returns
        -------
        tuple of data structure representations: (list, list, dict, dict)
        """
        if relationship_attributes:
            unique_relationships = self._relationship_keys(G, relationship_attributes)
        else:
            unique_relationships = [None]
        unique_relationships = list(unique_relationships)
        relationship_index_lookup = dict(
            (value, index) for index, value in enumerate(unique_relationships)
        )

        group_ids = list(self.group_ids)
        group_sets = [set(s) for s in self.group_sets]

        group_lookup = dict()
        for group_id, group in zip(group_ids, group_sets):
            for node in group:
                group_lookup[node] = group_id

        bitmap, participation_counts = self._calculate_bitmap(
            G,
            group_ids,
            group_sets,
            relationship_attributes,
            relationship_index_lookup,
            group_lookup,
        )

        while any(
            self._is_eligible(group_ids, group_sets, participation_counts, g_id)
            for g_id in group_ids
        ):
            group_ids, group_sets = self._split(
                G,
                group_ids,
                group_sets,
                relationship_attributes,
                bitmap,
                participation_counts,
                group_lookup,
            )
            bitmap, participation_counts = self._calculate_bitmap(
                G,
                group_ids,
                group_sets,
                relationship_attributes,
                relationship_index_lookup,
                group_lookup,
            )

        return (
            group_ids,
            group_sets,
            participation_counts,
            bitmap,
            relationship_index_lookup,
        )

    @staticmethod
    def _is_eligible(group_ids, group_sets, participation_counts, group_id):
        """
        Determines if a group is AR-compatible.

        A group is AR-compatible when all of the nodes in the group have the
        same node attributes, and all nodes have relationships with the same
        other groups.

        Parameters
        ----------
        group_ids: iterable
            Group ids of the current graph summary
        group_sets: iterable
            Group membership of nodes in the current graph summary
        participation_counts: dict
            ID of group
        group_id: int
            ID of group

        Returns
        -------
        boolean
        """
        group_size = len(group_sets[group_id])
        for other_group_id in group_ids:
            group_relationships = participation_counts[group_id][other_group_id]
            if any(
                relationship_count != 0 and relationship_count != group_size
                for relationship_count in group_relationships
            ):
                return True
        return False

    def _split(
        self,
        G,
        group_ids,
        group_sets,
        relationship_attributes,
        bitmap,
        participation_counts,
        group_lookup,
        group_id=None,
    ):
        """
        Splits the group with the given group_id based on the relationships
        of the nodes so that each new grouping will all have the same
        relationships with other nodes.

        Parameters
        ----------
        G: graph
            Networkx Graph to be summarized
        group_ids: iterable
            Group ids of the current graph summary
        group_sets: iterable
            Group membership of nodes

        Returns:
            None
        """
        if not group_id:
            eligible_group_ids = set(
                group_id
                for group_id in group_ids
                if self._is_eligible(
                    group_ids, group_sets, participation_counts, group_id
                )
            )
            group_id = eligible_group_ids.pop()

        logger.debug("Splitting group %r: %r", group_id, group_sets[group_id])
        new_group_mappings = dict()
        for node in group_sets[group_id]:
            signature = []
            for grouping in bitmap[node]:
                signature += grouping
            signature = tuple(signature)
            new_group_mappings.setdefault(signature, set())
            new_group_mappings[signature].add(node)
        new_groups = list(new_group_mappings.values())
        logger.debug(
            "Split group %i into %i groups: %r", group_id, len(new_groups), new_groups
        )
        return self._update_groups(
            group_ids,
            group_sets,
            relationship_attributes,
            group_id,
            new_groups[1:],
            group_lookup,
        )
