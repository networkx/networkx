"""Functions involving natural generalizations of the minimum cut problem."""

import itertools
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["minimum_multiway_cut", "minimum_k_cut"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def minimum_multiway_cut(G, terminals, weight=None):
    """Compute an approximated Minimum Multiway Cut and the corresponding cut value.

    Given an undirected graph $G = (V, E)$ and a set of terminals
    $S = \{s_1, s_2, \dots ,s_k\} \subseteq V$, a multiway cut is a set of edges
    whose removal disconnects the terminals from each other.
    The min-multiway cut problem asks for the minimum weight multiway cut.
    The function computes a $(2-\\frac{2}{k})$-approximated Minimum Multiway Cut with $k$ being
    the number of terminals.

    Note that the case in which $k=2$ corresponds to the minimum $(s,t)$-cut and can
    be solved optimally in polynomial time. For $k \geq 3$, the problem is NP-hard [2]_.

    The function implements the algorithm described in [1]_. The algorithm is based on the concept
    of isolating cuts. An *isolating cut* for $s_i \in S$ is a set of edges whose removal disconnects
    $s_i$ from all $s_j \\in S$ with $j \\neq i$.

    The algorithm can be summarised as follows.

    1. For each $i=1, \dots, k$ compute a minimum weight isolating cut for $s_i$.
    2. Discard the heaviest of these cuts and output the union of the rest.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph.

    terminals : container of nodes
        A container with a subset of nodes of G.

    weight : string, optional (default = None)
        If None, every node has weight 1. If a string, use this node
        attribute as the node weight. A node without this attribute is
        assumed to have weight 1.

    Returns
    -------
    cut_value : scalar
        Value of the (approximated) minimum multiway cut.

    cutset : set
        Set of edges that, if removed from the graph, disconnects each
         terminal from all the others.

    Raises
    ------
    NetworkXNotImplemented
        If G is directed or a mutigraph
    NetworkXError
        If G is empty or
        If G is not connected or
        If the number of terminals is smaller than 2.

    References
    ----------
    .. [1]  Vazirani, Vijay V. *Approximation algorithms*.
            Springer Science & Business Media, 2013.
    .. [2]  Dahlhaus, Elias, et al. *The complexity of multiway cuts*.
            Proceedings of the twenty-fourth annual ACM symposium on Theory of computing. 1992
    """
    if not G:
        raise nx.NetworkXError("Expected non-empty NetworkX graph!")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    # only consider the terminals in G
    terminals = set(terminals) & G.nodes()
    # raise an error if less than two terminal have been provided
    if len(terminals) < 2:
        raise nx.NetworkXError("At least two terminals should be provided.")

    # extract edges weight, and set edges weights with no attribute to 1
    edges_weights = G.edges(data=weight, default=1)
    # create a new Graph G2
    G2 = nx.Graph()
    G2.add_weighted_edges_from(edges_weights, weight="capacity")

    # take a non-existing node of G to be the sink
    sink = next(u for u in range(len(G) + 1) if u not in G)
    # add edges from the terminals to the sink node with infinite capacity
    G2.add_edges_from([(u, sink) for u in terminals], capacity=float("inf"))

    all_cuts = []
    # compute the minimum weight isolating cut for each terminal
    for u in terminals:
        # remove the edge from u to the sink
        G2.remove_edge(u, sink)
        # get the cut value and the 2 partitions of nodes
        value_cut, (p1, p2) = nx.minimum_cut(G2, u, sink)
        # get the edges crossing the cut
        edges_cut = set(nx.edge_boundary(G2, p1, p2))
        # add to the result
        all_cuts.append((edges_cut, value_cut))
        # re-add the edge to the sink
        G2.add_edge(u, sink, capacity=float("inf"))

    # discard the heaviest cut and take the union of the rest
    cutset = set()
    cut_value = 0
    for u, v in itertools.chain.from_iterable(
        el[0] for el in sorted(all_cuts, key=lambda x: x[1])[:-1]
    ):
        if (u, v) not in cutset and (v, u) not in cutset:
            # add to the cutset
            cutset.add((u, v))
            # add the weight to the cut cost
            cut_value += G2.edges[u, v]["capacity"]

    return cut_value, cutset


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def minimum_k_cut(G, k, weight=None):
    """Compute an approximated Minimum k-Cut and the corresponding cut value.

    Given an undirected graph $G = (V, E)$ and an integer $k \geq 2$, a $k$-cut is a
    set of edges whose removal leaves at least $k$ connected components.
    The Min-$k$-cut problem asks for a minimum weight $k$-cut.
    The function computes a $(2-\\frac{2}{k})$-approximated Minimum k-Cut.

    Note that the case in which $k=2$ corresponds to the global minimum cut and can
    be solved optimally in polynomial time. For $k \geq 3$, it's NP-hard [1]_.

    The function implements the algorithm described in [1]_.  The algorithm is based on
    the concept of Gomory-Hu trees (see :meth:`networkx.algorithms.flow.gomory_hu_tree`)
    for finding a light k-cut.

    The algorithm can be summarised as follows.

    1. Compute a Gomory-Hu tree T starting from G.
    2. Take the union of the $k − 1$ lightest cuts from the $n − 1$ cuts associated with
       the edges in $T$. A cut associated with an edge $(u,v)$ of $T$ is a cut that connects the two
       connected components obtained by removing $(u,v)$ from $T$.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph.

    k : integer
        The number of connected components the graph should have
        when the edges of the cut are removed.

    weight : string, optional (default = None)
        If None, every edge has weight 1. If a string, use this edge
        attribute as the edge weight. An edge without this attribute is
        assumed to have weight 1.

    Returns
    -------
    cut_value : scalar
        Value of the (approximated) minimum k-cut.

    cutset : set
        Set of edges whose removal leaves at least k connected components.

    Raises
    ------
    NetworkXNotImplemented
        If G is directed or a mutigraph
    NetworkXError
        If G is empty or
        If G is not connected or
        If k is smaller than 1 or greater than the number of nodes of G.

    Notes
    -----
    The removal of the cutset from G will leave *at least* $k$ components.
    If more than $k$ components are created then it's enough to throw back
    some of the removed edges until there are exactly $k$ components.

    See also
    --------
    networkx.algorithms.flow.minimum_cut
    networkx.algorithms.flow.gomory_hu_tree

    References
    ----------
    .. [1]  Vazirani, Vijay V. *Approximation algorithms*.
            Springer Science & Business Media, 2013.
    """
    if not G:
        raise nx.NetworkXError("Expected non-empty NetworkX graph!")
    if not nx.is_connected(G):
        raise nx.NetworkXError("Graph not connected.")
    if not 1 <= k <= len(G):
        raise nx.NetworkXError(f"k should be within 1 and {len(G)}")

    # extract edges weights, and set edges weights with no attribute to 1
    edges_weights = G.edges(data=weight, default=1)
    # create a new Graph G2
    G2 = nx.Graph()
    G2.add_weighted_edges_from(edges_weights, weight="capacity")

    # build a Gomory-Hu tree T from G
    T = nx.gomory_hu_tree(G2)
    # get the k-1 cheapest edges of the Gomory-Hu tree
    min_weight_edges = sorted(T.edges(data="weight"), key=lambda x: x[2])[: k - 1]

    # compute the cutset, the value is computed after as an edge might appear more than once
    all_edges_cut = set()
    for u, v, _ in min_weight_edges:
        # remove (u,v) from the tree
        T.remove_edge(u, v)
        # get the connected component that contains u
        p1 = nx.node_connected_component(T, u)
        # add the boundary edges of p1 to the cutset
        all_edges_cut |= set(nx.edge_boundary(G2, p1))
        # re-add (u,v) to the tree
        T.add_edge(u, v)

    # consider edges only in a direction
    cutset = set()
    cut_value = 0
    for u, v in all_edges_cut:
        if (u, v) not in cutset and (v, u) not in cutset:
            # add to the cutset
            cutset.add((u, v))
            # add the weight to the cut cost
            cut_value += G2.edges[u, v]["capacity"]

    return cut_value, cutset
