"""Functions for measuring the quality of a partition (into
communities).

"""

from functools import wraps
from itertools import product

import networkx as nx
from networkx import NetworkXError
from networkx.utils import not_implemented_for
from networkx.algorithms.community.community_utils import is_partition

__all__ = ["coverage", "modularity", "performance"]


class NotAPartition(NetworkXError):
    """Raised if a given collection is not a partition.

    """

    def __init__(self, G, collection):
        msg = f"{G} is not a valid partition of the graph {collection}"
        super().__init__(msg)


def require_partition(func):
    """Decorator to check that a valid partition is input to a function

    Raises :exc:`networkx.NetworkXError` if the partition is not valid.

    This decorator should be used on functions whose first two arguments
    are a graph and a partition of the nodes of that graph (in that
    order)::

        >>> @require_partition
        ... def foo(G, partition):
        ...     print("partition is valid!")
        ...
        >>> G = nx.complete_graph(5)
        >>> partition = [{0, 1}, {2, 3}, {4}]
        >>> foo(G, partition)
        partition is valid!
        >>> partition = [{0}, {2, 3}, {4}]
        >>> foo(G, partition)
        Traceback (most recent call last):
          ...
        networkx.exception.NetworkXError: `partition` is not a valid partition of the nodes of G
        >>> partition = [{0, 1}, {1, 2, 3}, {4}]
        >>> foo(G, partition)
        Traceback (most recent call last):
          ...
        networkx.exception.NetworkXError: `partition` is not a valid partition of the nodes of G

    """

    @wraps(func)
    def new_func(*args, **kw):
        # Here we assume that the first two arguments are (G, partition).
        if not is_partition(*args[:2]):
            raise nx.NetworkXError(
                "`partition` is not a valid partition of" " the nodes of G"
            )
        return func(*args, **kw)

    return new_func


def intra_community_edges(G, partition):
    """Returns the number of intra-community edges for a partition of `G`.

    Parameters
    ----------
    G : NetworkX graph.

    partition : iterable of sets of nodes
        This must be a partition of the nodes of `G`.

    The "intra-community edges" are those edges joining a pair of nodes
    in the same block of the partition.

    """
    return sum(G.subgraph(block).size() for block in partition)


def inter_community_edges(G, partition):
    """Returns the number of inter-community edges for a prtition of `G`.
    according to the given
    partition of the nodes of `G`.

    Parameters
    ----------
    G : NetworkX graph.

    partition : iterable of sets of nodes
        This must be a partition of the nodes of `G`.

    The *inter-community edges* are those edges joining a pair of nodes
    in different blocks of the partition.

    Implementation note: this function creates an intermediate graph
    that may require the same amount of memory as that of `G`.

    """
    # Alternate implementation that does not require constructing a new
    # graph object (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in G.edges() if aff[u] != aff[v])
    #
    MG = nx.MultiDiGraph if G.is_directed() else nx.MultiGraph
    return nx.quotient_graph(G, partition, create_using=MG).size()


def inter_community_non_edges(G, partition):
    """Returns the number of inter-community non-edges according to the
    given partition of the nodes of `G`.

    `G` must be a NetworkX graph.

    `partition` must be a partition of the nodes of `G`.

    A *non-edge* is a pair of nodes (undirected if `G` is undirected)
    that are not adjacent in `G`. The *inter-community non-edges* are
    those non-edges on a pair of nodes in different blocks of the
    partition.

    Implementation note: this function creates two intermediate graphs,
    which may require up to twice the amount of memory as required to
    store `G`.

    """
    # Alternate implementation that does not require constructing two
    # new graph objects (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in nx.non_edges(G) if aff[u] != aff[v])
    #
    return inter_community_edges(nx.complement(G), partition)


@not_implemented_for("multigraph")
@require_partition
def performance(G, partition):
    """Returns the performance of a partition.

    The *performance* of a partition is the ratio of the number of
    intra-community edges plus inter-community non-edges with the total
    number of potential edges.

    Parameters
    ----------
    G : NetworkX graph
        A simple graph (directed or undirected).

    partition : sequence
        Partition of the nodes of `G`, represented as a sequence of
        sets of nodes. Each block of the partition represents a
        community.

    Returns
    -------
    float
        The performance of the partition, as defined above.

    Raises
    ------
    NetworkXError
        If `partition` is not a valid partition of the nodes of `G`.

    References
    ----------
    .. [1] Santo Fortunato.
           "Community Detection in Graphs".
           *Physical Reports*, Volume 486, Issue 3--5 pp. 75--174
           <https://arxiv.org/abs/0906.0612>

    """
    # Compute the number of intra-community edges and inter-community
    # edges.
    intra_edges = intra_community_edges(G, partition)
    inter_edges = inter_community_non_edges(G, partition)
    # Compute the number of edges in the complete graph (directed or
    # undirected, as it depends on `G`) on `n` nodes.
    #
    # (If `G` is an undirected graph, we divide by two since we have
    # double-counted each potential edge. We use integer division since
    # `total_pairs` is guaranteed to be even.)
    n = len(G)
    total_pairs = n * (n - 1)
    if not G.is_directed():
        total_pairs //= 2
    return (intra_edges + inter_edges) / total_pairs


@require_partition
def coverage(G, partition):
    """Returns the coverage of a partition.

    The *coverage* of a partition is the ratio of the number of
    intra-community edges to the total number of edges in the graph.

    Parameters
    ----------
    G : NetworkX graph

    partition : sequence
        Partition of the nodes of `G`, represented as a sequence of
        sets of nodes. Each block of the partition represents a
        community.

    Returns
    -------
    float
        The coverage of the partition, as defined above.

    Raises
    ------
    NetworkXError
        If `partition` is not a valid partition of the nodes of `G`.

    Notes
    -----
    If `G` is a multigraph, the multiplicity of edges is counted.

    References
    ----------
    .. [1] Santo Fortunato.
           "Community Detection in Graphs".
           *Physical Reports*, Volume 486, Issue 3--5 pp. 75--174
           <https://arxiv.org/abs/0906.0612>

    """
    intra_edges = intra_community_edges(G, partition)
    total_edges = G.number_of_edges()
    return intra_edges / total_edges


def modularity(G, communities, weight="weight"):
    r"""Returns the modularity of the given partition of the graph.

    Modularity is defined in [1]_ as

    .. math::

        Q = \frac{1}{2m} \sum_{ij} \left( A_{ij} - \frac{k_ik_j}{2m}\right)
            \delta(c_i,c_j)

    where $m$ is the number of edges, $A$ is the adjacency matrix of
    `G`, $k_i$ is the degree of $i$ and $\delta(c_i, c_j)$
    is 1 if $i$ and $j$ are in the same community and 0 otherwise.

    According to [2]_ (and verified by some algebra) this can be reduced to

    .. math::
       Q = \sum_{c=1}^{n}
       \left[ \frac{L_c}{m} - \left( \frac{k_c}{2m} \right) ^2 \right]

    where the sum iterates over all communities $c$, $m$ is the number of edges,
    $L_c$ is the number of intra-community links for community $c$,
    $k_c$ is the sum of degrees of the nodes in community $c$.

    The second formula is the one actually used in calculation of the modularity.

    Parameters
    ----------
    G : NetworkX Graph

    communities : list or iterable of set of nodes
        These node sets must represent a partition of G's nodes.

    weight : string or None, optional (default="weight")
            The edge attribute that holds the numerical value used
            as a weight. If None or an edge does not have that attribute,
            then that edge has weight 1.

    Returns
    -------
    Q : float
        The modularity of the paritition.

    Raises
    ------
    NotAPartition
        If `communities` is not a partition of the nodes of `G`.

    Examples
    --------
    >>> import networkx.algorithms.community as nx_comm
    >>> G = nx.barbell_graph(3, 0)
    >>> nx_comm.modularity(G, [{0, 1, 2}, {3, 4, 5}])
    0.35714285714285715
    >>> nx_comm.modularity(G, nx_comm.label_propagation_communities(G))
    0.35714285714285715

    References
    ----------
    .. [1] M. E. J. Newman *Networks: An Introduction*, page 224.
       Oxford University Press, 2011.
    .. [2] Clauset, Aaron, Mark EJ Newman, and Cristopher Moore.
       "Finding community structure in very large networks."
       Physical review E 70.6 (2004). <https://arxiv.org/abs/cond-mat/0408187>
    """
    if not isinstance(communities, list):
        communities = list(communities)
    if not is_partition(G, communities):
        raise NotAPartition(G, communities)

    directed = G.is_directed()
    if directed:
        out_degree = dict(G.out_degree(weight=weight))
        in_degree = dict(G.in_degree(weight=weight))
        m = sum(out_degree.values())
        norm = 1 / m ** 2
    else:
        out_degree = in_degree = dict(G.degree(weight=weight))
        deg_sum = sum(out_degree.values())
        m = deg_sum / 2
        norm = 1 / deg_sum ** 2

    def community_contribution(community):
        comm = set(community)
        L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

        out_degree_sum = sum(out_degree[u] for u in comm)
        in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum

        return L_c / m - out_degree_sum * in_degree_sum * norm

    return sum(map(community_contribution, communities))
