"""
Functions for hashing graphs to strings.
Isomorphic graphs should be assigned identical hashes.
For now, only Weisfeiler-Lehman hashing is implemented.
"""

from collections import Counter, defaultdict
from hashlib import blake2b

__all__ = ["weisfeiler_lehman_graph_hash", "weisfeiler_lehman_subgraph_hashes"]


def _hash_label(label, digest_size):
    return blake2b(label.encode("ascii"), digest_size=digest_size).hexdigest()


def _init_node_labels(G, edge_attr, node_attr):
    if node_attr:
        return {u: str(dd[node_attr]) for u, dd in G.nodes(data=True)}
    elif edge_attr:
        return {u: "" for u in G}
    else:
        return {u: str(deg) for u, deg in G.degree()}


def _neighborhood_aggregate(G, node, node_labels, edge_attr=None):
    """
    Compute new labels for given node by aggregating
    the labels of each node's neighbors.
    """
    label_list = [node_labels[node]]
    for nbr in G.neighbors(node):
        prefix = "" if edge_attr is None else str(G[node][nbr][edge_attr])
        label_list.append(prefix + node_labels[nbr])
    return "".join(sorted(label_list))


def weisfeiler_lehman_graph_hash(
    G, edge_attr=None, node_attr=None, iterations=3, digest_size=16
):
    """Return Weisfeiler Lehman (WL) graph hash.

    The function iteratively aggregates and hashes neighbourhoods of each node.
    After each node's neighbors are hashed to obtain updated node labels,
    a hashed histogram of resulting labels is returned as the final hash.

    Hashes are identical for isomorphic graphs and strong guarantees that
    non-isomorphic graphs will get different hashes. See [1]_ for details.

    If no node or edge attributes are provided, the degree of each node
    is used as its initial label.
    Otherwise, node and/or edge labels are used to compute the hash.

    Parameters
    ----------
    G: graph
        The graph to be hashed.
        Can have node and/or edge attributes. Can also have no attributes.
    edge_attr: string, default=None
        The key in edge attribute dictionary to be used for hashing.
        If None, edge labels are ignored.
    node_attr: string, default=None
        The key in node attribute dictionary to be used for hashing.
        If None, and no edge_attr given, use the degrees of the nodes as labels.
    iterations: int, default=3
        Number of neighbor aggregations to perform.
        Should be larger for larger graphs.
    digest_size: int, default=16
        Size (in bits) of blake2b hash digest to use for hashing node labels.

    Returns
    -------
    h : string
        Hexadecimal string corresponding to hash of the input graph.

    Examples
    --------
    Two graphs with edge attributes that are isomorphic, except for
    differences in the edge labels.

    >>> G1 = nx.Graph()
    >>> G1.add_edges_from(
    ...     [
    ...         (1, 2, {"label": "A"}),
    ...         (2, 3, {"label": "A"}),
    ...         (3, 1, {"label": "A"}),
    ...         (1, 4, {"label": "B"}),
    ...     ]
    ... )
    >>> G2 = nx.Graph()
    >>> G2.add_edges_from(
    ...     [
    ...         (5, 6, {"label": "B"}),
    ...         (6, 7, {"label": "A"}),
    ...         (7, 5, {"label": "A"}),
    ...         (7, 8, {"label": "A"}),
    ...     ]
    ... )

    Omitting the `edge_attr` option, results in identical hashes.

    >>> nx.weisfeiler_lehman_graph_hash(G1)
    '3108a936907b3ee3704642f9eeab34fe'
    >>> nx.weisfeiler_lehman_graph_hash(G2)
    '3108a936907b3ee3704642f9eeab34fe'

    With edge labels, the graphs are no longer assigned
    the same hash digest.

    >>> nx.weisfeiler_lehman_graph_hash(G1, edge_attr="label")
    'd0819438f9cc0cd60ea93a6c70c2f939'
    >>> nx.weisfeiler_lehman_graph_hash(G2, edge_attr="label")
    '43e9b18eeb859b669ad2269ecc6d43bf'

    Notes
    -----
    To return the WL hashes of each subgraph of a graph, use
    `weisfeiler_lehman_subgraph_hashes`

    Similarity between hashes does not imply similarity between graphs.

    References
    ----------
    .. [1] Shervashidze, Nino, Pascal Schweitzer, Erik Jan Van Leeuwen,
       Kurt Mehlhorn, and Karsten M. Borgwardt. Weisfeiler Lehman
       Graph Kernels. Journal of Machine Learning Research. 2011.
       http://www.jmlr.org/papers/volume12/shervashidze11a/shervashidze11a.pdf

    See also
    --------
    weisfeiler_lehman_subgraph_hashes
    """

    def weisfeiler_lehman_step(G, labels, edge_attr=None):
        """
        Apply neighborhood aggregation to each node
        in the graph.
        Computes a dictionary with labels for each node.
        """
        new_labels = {}
        for node in G.nodes():
            label = _neighborhood_aggregate(G, node, labels, edge_attr=edge_attr)
            new_labels[node] = _hash_label(label, digest_size)
        return new_labels

    # set initial node labels
    node_labels = _init_node_labels(G, edge_attr, node_attr)

    subgraph_hash_counts = []
    for _ in range(iterations):
        node_labels = weisfeiler_lehman_step(G, node_labels, edge_attr=edge_attr)
        counter = Counter(node_labels.values())
        # sort the counter, extend total counts
        subgraph_hash_counts.extend(sorted(counter.items(), key=lambda x: x[0]))

    # hash the final counter
    return _hash_label(str(tuple(subgraph_hash_counts)), digest_size)


def weisfeiler_lehman_subgraph_hashes(
    G, edge_attr=None, node_attr=None, iterations=3, digest_size=16
):
    """Return a dictionary indexed by node, giving a list of Weisfeiler-Lehman
    (WL) hashes for each subgraph originating from each node, ordered by
    iteration depth.

    The function iteratively aggregates and hashes neighbourhoods of each node.
    This is achieved for each step by replacing for each node its label from
    the previous iteration with its hashed 1-hop neighborhood aggregate.
    The new node label is then appended to a list of node labels for each
    node.

    To aggregate neighborhoods at each step for a node $n$, all labels of
    nodes adjacent to $n$ are concatenated. If the `edge_attr` parameter is set,
    labels for each neighboring node are prefixed with the value of this attribute
    along the connecting edge from this neighbor to node $n$. The resulting string
    is then hashed to compress this information into a fixed digest size.

    Thus, at the $i$th iteration nodes within $2i$ distance influence any given
    hashed node label. We can therefore say that at depth $i$ for node $n$
    we have a hash for a subgraph induced by the $2i$-hop neighborhood of $n$.

    Can be used to to create general Weisfeiler-Lehman graph kernels, or
    generate features for graphs or nodes, for example to generate 'words' in a
    graph as seen in the 'graph2vec' algorithm.
    See [1]_ & [2]_ respectively for details.

    Hashes are identical for isomorphic subgraphs and there exist strong
    guarantees that non-isomorphic graphs will get different hashes.
    See [1]_ for details.

    If no node or edge attributes are provided, the degree of each node
    is used as its initial label.
    Otherwise, node and/or edge labels are used to compute the hash.

    Parameters
    ----------
    G: graph
        The graph to be hashed.
        Can have node and/or edge attributes. Can also have no attributes.
    edge_attr: string, default=None
        The key in edge attribute dictionary to be used for hashing.
        If None, edge labels are ignored.
    node_attr: string, default=None
        The key in node attribute dictionary to be used for hashing.
        If None, and no edge_attr given, use the degrees of the nodes as labels.
    iterations: int, default=3
        Number of neighbor aggregations to perform.
        Should be larger for larger graphs.
    digest_size: int, default=16
        Size (in bits) of blake2b hash digest to use for hashing node labels.
        The default size is 16 bits

    Returns
    -------
    node_subgraph_hashes : dict
        A dictionary with each key given by a node in G, and each value given
        by the subgraph hashes in order of depth from the key node.

    Examples
    --------
    Finding similar nodes in different graphs:
    >>> G1 = nx.Graph()
    >>> G1.add_edges_from([
    ...     (1, 2), (2, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 7)
    ... ])
    >>> G2 = nx.Graph()
    >>> G2.add_edges_from([
    ...     (1, 3), (2, 3), (1, 6), (1, 5), (4, 6)
    ... ])
    >>> g1_hashes = nx.weisfeiler_lehman_subgraph_hashes(G1, iterations=3, digest_size=8)
    >>> g2_hashes = nx.weisfeiler_lehman_subgraph_hashes(G2, iterations=3, digest_size=8)

    Even though G1 and G2 are not isomorphic (they have different numbers of edges),
    the hash sequence of depth 3 for node 1 in G1 and node 5 in G2 are similar:

    >>> g1_hashes[1]
    ['a93b64973cfc8897', 'c82391d740bfbe09', 'd45fb49e284520c3']
    >>> g2_hashes[5]
    ['a93b64973cfc8897', 'c82391d740bfbe09', '3f26cdb3d5ad86e7']

    The first 2 WL subgraph hashes match. From this we can conclude that it's very
    likely the neighborhood of 4 hops around these nodes are isomorphic: each
    iteration aggregates 1-hop neighbourhoods meaning hashes at depth $n$ are influenced
    by every node within $2n$ hops.

    However the neighborhood of 6 hops is no longer isomorphic since their 3rd hash does
    not match.

    These nodes may be candidates to be classified together since their local topology
    is similar.

    Notes
    -----
    To hash the full graph when subgraph hashes are not needed, use
    `weisfeiler_lehman_graph_hash` for efficiency.

    Similarity between hashes does not imply similarity between graphs.

    References
    -------
    .. [1] Shervashidze, Nino, Pascal Schweitzer, Erik Jan Van Leeuwen,
       Kurt Mehlhorn, and Karsten M. Borgwardt. Weisfeiler Lehman
       Graph Kernels. Journal of Machine Learning Research. 2011.
       http://www.jmlr.org/papers/volume12/shervashidze11a/shervashidze11a.pdf
    .. [2] Annamalai Narayanan, Mahinthan Chandramohan, Rajasekar Venkatesan,
       Lihui Chen, Yang Liu and Shantanu Jaiswa. graph2vec: Learning
       Distributed Representations of Graphs. arXiv. 2017
       https://arxiv.org/pdf/1707.05005.pdf

    See also
    --------
    weisfeiler_lehman_graph_hash
    """

    def weisfeiler_lehman_step(G, labels, node_subgraph_hashes, edge_attr=None):
        """
        Apply neighborhood aggregation to each node
        in the graph.
        Computes a dictionary with labels for each node.
        Appends the new hashed label to the dictionary of subgraph hashes
        originating from and indexed by each node in G
        """
        new_labels = {}
        for node in G.nodes():
            label = _neighborhood_aggregate(G, node, labels, edge_attr=edge_attr)
            hashed_label = _hash_label(label, digest_size)
            new_labels[node] = hashed_label
            node_subgraph_hashes[node].append(hashed_label)
        return new_labels

    node_labels = _init_node_labels(G, edge_attr, node_attr)

    node_subgraph_hashes = defaultdict(list)
    for _ in range(iterations):
        node_labels = weisfeiler_lehman_step(
            G, node_labels, node_subgraph_hashes, edge_attr
        )

    return dict(node_subgraph_hashes)
