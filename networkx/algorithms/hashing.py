"""
    Functions for hashing graphs to strings.
    Isomorphic graphs should be assigned identical hashes.
    For now, only Weisfeiler-Lehman hashing is implemented.
"""

from collections import Counter
from hashlib import blake2b

__all__ = [
    "wl_hash",
]

def wl_hash(G, edge_attr=None, node_attr=None, iterations=3, digest_size=16):
    """
    Returns WL hash of a graph.
    We iteratively aggregate and hash neighbourhoods of each node.
    After each node's neighbors are hashed to obtain updated node labels,
    we hash a histogram of resulting labels as the final hash.
    Implementation of (http://jmlr.org/papers/volume12/shervashidze11a/shervashidze11a.pdf)
    Parameters
    ----------
    G: graph
        The graph to be hashed. Can have node and/or edge attributes. Can also have no attributes.
    edge_attr: string
        The key in edge attribute dictionary to be used for hashing. If None, edge labels are ignored.
    node_attr: string
        The key in node attribute dictionary to be used for hashing. If None, and no edge_attr given, use
        degree of node as label.
    iterations: int
        Number of neighbor aggregations to perform. Should be larger for larger graphs.
    digest_size: int
        Size of blake2b hash digest to use for hashing node labels.
    In example below, we have two triangle graphs with a tail node that are isomorphic except for edge labels.
    By specifying the edge_attr option, the graphs receive different hashes.
    Returns
    -------
    h : string
        Hexadecimal string corresponding to hash of the input graph.
    >>> import networkx as nx
    >>> G1 = nx.Graph()
    >>> G1.add_edges_from([(1, 2, {'label': 'A'}),\
                           (2, 3, {'label': 'A'}),\
                           (3, 1, {'label': 'A'}),\
                           (1, 4, {'label': 'B'})])
    >>> G2 = nx.Graph()
    >>> G2.add_edges_from([(5,6, {'label': 'B'}),\
                           (6,7, {'label': 'A'}),\
                           (7,5, {'label': 'A'}),\
                           (7,8, {'label': 'A'})])
    >>> wl_hash(G1) == wl_hash(G2)
    True
    >>> wl_hash(G1, edge_attr='label') == wl_hash(G2, edge_attr='label')
    False
    """

    def nei_agg(G, n, node_labels, edge_attr=None):
        x = [node_labels[n]]
        for nei in G.neighbors(n):
            prefix = "" if not edge_attr else G[n][nei][edge_attr]
            x.append(prefix + node_labels[nei])
        return ''.join(sorted(x))

    def wl_step(G, labels, edge_attr=None, node_attr=None):
        """
            Aggregate neighbor labels and edge label.
        """
        new_labels = dict()
        for n in G.nodes():
            new_labels[n] = nei_agg(G, n, labels, edge_attr=edge_attr)
        return new_labels

    items = []
    node_labels = dict()
    # set initial node labels
    for n in G.nodes():
        if (not node_attr) and (not edge_attr):
            node_labels[n] = str(G.degree(n))
        elif node_attr:
            node_labels[n] = str(G.nodes[n][node_attr])
        else:
            node_labels[n] = ''

    for k in range(iterations):
        node_labels = wl_step(G, node_labels, edge_attr=edge_attr)
        c = Counter()
        # count node labels
        for node, d in node_labels.items():
            h = blake2b(digest_size=digest_size)
            h.update(d.encode('ascii'))
            c.update([h.hexdigest()])
        # sort the counter, extend total counts
        items.extend(sorted(c.items(), key=lambda x: x[0]))

    # hash the final counter
    h = blake2b(digest_size=digest_size)
    h.update(str(tuple(items)).encode('ascii'))
    h = h.hexdigest()
    return h
