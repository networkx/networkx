import logging
from collections import deque

import networkx as nx

from ..d_separation import _bfs_with_marks
from .mixed_edge_moral import mixed_edge_moral_graph

__all__ = ["m_separated", "minimal_m_separator", "is_minimal_m_separator"]

logger = logging.getLogger(__name__)


def m_separated(
    G,
    x,
    y,
    z,
    directed_edge_name="directed",
    bidirected_edge_name="bidirected",
    undirected_edge_name="undirected",
):
    """Check m-separation among 'x' and 'y' given 'z' in mixed-edge causal graph G, which may
    contain directed, bidirected, and undirected edges.

    This implements the m-separation algorithm TESTSEP presented in [1]_ for ancestral mixed
    graphs. Further checks have ensure that it works for non-ancestral mixed graphs
    (e.g. ADMGs). The algorithm performs a breadth-first search over m-connecting paths
    between 'x' and 'y' (i.e. a path on which every node that is a collider is in 'z', and
    every node that is not a collider is not in 'z'). The algorithm has runtime
    :math:`O(|E| + |V|)` for number of edges :math:`|E|` and number of vertices :math:`|V|`.


    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    x : set
        First set of nodes in ``G``.
    y : set
        Second set of nodes in ``G``.
    z : set
        Set of conditioning nodes in ``G``. Can be empty set.
    directed_edge_name : str
        Name of the directed edge, default is directed.
    bidirected_edge_name : str
        Name of the bidirected edge, default is bidirected.
    undirected_edge_name : str
        Name of the undirected edge, default is undirected.

    Returns
    -------
    b : bool
        A boolean that is true if ``x`` is m-separated from ``y`` given ``z`` in ``G``.

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.


    See Also
    --------
    networkx.algorithms.d_separation.d_separated

    Notes
    -----
    This wraps the networkx implementation, which only allows DAGs and does
    not have an ``ADMG`` representation.
    """
    if not isinstance(G, nx.MixedEdgeGraph):
        raise nx.NetworkXError(
            "m-separation should only be run on a MixedEdgeGraph. If "
            'you have a directed graph, use "d_separated" function instead.'
        )
    if not set(G.edge_types).issubset(
        {directed_edge_name, bidirected_edge_name, undirected_edge_name}
    ):
        raise nx.NetworkXError(
            f"m-separation only works on graphs with directed, bidirected, and undirected edges. "
            f"Your graph passed in has the following edge types: {G.edge_types}, whereas "
            f"the function is expecting directed edges named {directed_edge_name}, "
            f"bidirected edges named {bidirected_edge_name}, and undirected edges "
            f"named {undirected_edge_name}."
        )

    if directed_edge_name in G.edge_types:
        if not nx.is_directed_acyclic_graph(G.get_graphs(directed_edge_name)):
            raise nx.NetworkXError("directed edge graph should be directed acyclic")

    # contains -> and <-> edges from starting node T
    forward_deque = deque([])
    forward_visited = set()

    # contains <- and - edges from starting node T
    backward_deque = deque(x)
    backward_visited = set()
    has_undirected = undirected_edge_name in G.edge_types
    if has_undirected:
        G_undirected = G.get_graphs(edge_type=undirected_edge_name)
    has_directed = directed_edge_name in G.edge_types

    an_z = z
    if has_directed:
        G_directed = G.get_graphs(edge_type=directed_edge_name)
        an_z = set().union(*[nx.ancestors(G_directed, x) for x in z]).union(z)

    has_bidirected = bidirected_edge_name in G.edge_types
    if has_bidirected:
        G_bidirected = G.get_graphs(edge_type=bidirected_edge_name)

    while forward_deque or backward_deque:

        if backward_deque:
            node = backward_deque.popleft()
            backward_visited.add(node)
            if node in y:
                return False
            if node in z:
                continue

            # add - edges to forward deque
            if has_undirected:
                for nbr in G_undirected.neighbors(node):
                    if nbr not in backward_visited:
                        backward_deque.append(nbr)

            if has_directed:
                # add <- edges to backward deque
                for x, _ in G_directed.in_edges(nbunch=node):
                    if x not in backward_visited:
                        backward_deque.append(x)

                # add -> edges to forward deque
                for _, x in G_directed.out_edges(nbunch=node):
                    if x not in forward_visited:
                        forward_deque.append(x)

            # add <-> edge to forward deque
            if has_bidirected:
                for nbr in G_bidirected.neighbors(node):
                    if nbr not in forward_visited:
                        forward_deque.append(nbr)

        if forward_deque:
            node = forward_deque.popleft()
            forward_visited.add(node)
            if node in y:
                return False

            # Consider if *-> node <-* is opened due to conditioning on collider,
            # or descendant of collider
            if node in an_z:

                if has_directed:
                    # add <- edges to backward deque
                    for x, _ in G_directed.in_edges(nbunch=node):
                        if x not in backward_visited:
                            backward_deque.append(x)

                # add <-> edge to backward deque
                if has_bidirected:
                    for nbr in G_bidirected.neighbors(node):
                        if nbr not in forward_visited:
                            forward_deque.append(nbr)

            if node not in z:
                if has_undirected:
                    for nbr in G_undirected.neighbors(node):
                        if nbr not in backward_visited:
                            backward_deque.append(nbr)

                if has_directed:
                    # add -> edges to forward deque
                    for _, x in G_directed.out_edges(nbunch=node):
                        if x not in forward_visited:
                            forward_deque.append(x)

    return True


def _anterior(
    G, start_nodes, directed_edge_name="directed", undirected_edge_name="undirected"
):
    """Computes the anterior of a set of nodes in a graph with directed and undirected edges.

    This algorithm works through breadth-first search on mixed edge graphs with directed
    and undirected edges.

    All directed paths are ancestral and anterior. A path is also anterior if undirected edges
    could be replaced by directed edges to form a directed path. By definition, the anterior
    set includes the start nodes.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    start_nodes : set
        Set of nodes which are always included in the found separating set.
    directed_edge_name : str
        Name of the directed edge, default is directed.
    undirected_edge_name : str
        Name of the undirected edge, default is undirected.

    Returns
    -------
    visited : set
        The anterior set of nodes

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.
    """

    queue = deque(start_nodes)
    visited = set()

    has_undirected = undirected_edge_name in G.edge_types
    if has_undirected:
        G_undirected = G.get_graphs(edge_type=undirected_edge_name)
    has_directed = directed_edge_name in G.edge_types
    if has_directed:
        G_directed = G.get_graphs(edge_type=directed_edge_name)

    while queue:
        m = queue.popleft()
        if has_directed:
            for x, _ in G_directed.in_edges(nbunch=m):
                if x not in visited:
                    queue.append(x)
                    visited.add(x)
        if has_undirected:
            for x in G_undirected.neighbors(m):
                if x not in visited:
                    queue.append(x)
                    visited.add(x)

    return visited.union(start_nodes)


def is_minimal_m_separator(
    G,
    x,
    y,
    z,
    i=None,
    r=None,
    directed_edge_name="directed",
    bidirected_edge_name="bidirected",
    undirected_edge_name="undirected",
):
    """Check if a set 'z' is a i-minimal m-separator between 'x' and 'y'.

    The function will first check if 'z' is a m-separator, and then check if it
    is minimal. An i-minimal m-separating set is a minimal m-separator that contains i.

    This implements the algorithm TESTMINSEP presented in [1]_ for ancestral mixed graphs, but has
    been tested to work with non-ancestral graphs.

    This implementation differs from the specification of TESTMINSEP in [1]_ in that we replace
    the check in line 6 with :math:`z - i \\neq R_x`, and similarly in line 8 with
    :math:`z - i \\neq R_y`. This change was deemed necessary because in line 4 all nodes in ``i``
    are removed, so there cannot be paths from ``x`` to ``i`` in the augmented moralized graph,
    causing the algorithm to return false when a minimal m-separator existed.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    x : node
        Node in ``G``.
    y : node
        Node in ``G``.
    z : set
        Set of nodes in ``G`` representing the candidate minimal m-separator of ``x`` and ``y``.
    i : set
        Set of nodes which are always included in the found separating set,
        default is None, which is later set to empty set.
    r : set
        Largest set of nodes which may be included in the found separating set,
        default is None, which is later set to all vertices in ``G``.
    directed_edge_name : str
        Name of the directed edge, default is 'directed'.
    bidirected_edge_name : str
        Name of the bidirected edge, default is 'bidirected'.
    undirected_edge_name : str
        Name of the undirected edge, default is 'undirected'.

    Returns
    -------
    is_minimal_m_sep : bool
        If the set ``z`` is a minimal m-separator, returns True, else returns False.

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.

    """
    if i is None:
        i = set()
    if r is None:
        r = set(G.nodes())
    if not i <= z:
        raise nx.NetworkXError(
            f"Minimal set {i} should be no larger than proposed separating set {z}"
        )
    if not z <= r:
        raise nx.NetworkXError(
            f"Separating set {z} should be no larger than maximum set {r}"
        )

    if z - _anterior(G, {x, y}.union(i)) != set() or not z <= r:
        return False
    if not m_separated(
        G, x, y, z, directed_edge_name, bidirected_edge_name, undirected_edge_name
    ):
        return False

    G_copy = G.copy()

    nodeset = {x, y}.union(i)

    anterior_nodes_G = _anterior(G_copy, nodeset)
    G_copy.remove_nodes_from(set(G.nodes()) - anterior_nodes_G)
    aug_G_p = mixed_edge_moral_graph(
        G_copy,
        directed_edge_name=directed_edge_name,
        bidirected_edge_name=bidirected_edge_name,
        undirected_edge_name=undirected_edge_name,
    )
    for node in i:
        aug_G_p.remove_node(node)

    r_x = _bfs_with_marks(aug_G_p, x, z)

    # Note: we check z - i != r_x instead of z != r_x since
    # all nodes in i are removed from graph and so x will never have a path
    # to i. Appears to be bug in the original algorithm.
    if z - i != r_x:
        return False
    r_y = _bfs_with_marks(aug_G_p, y, z)

    # Note: we check z - i != r_y for similar reasons as above.
    if z - i != r_y:
        return False

    return True


def minimal_m_separator(
    G,
    x,
    y,
    i=None,
    r=None,
    directed_edge_name="directed",
    bidirected_edge_name="bidirected",
    undirected_edge_name="undirected",
):
    """Find a i-minimal m-separating set 'z' between 'x' and 'y' in mixed-edge causal graph G.

    The set which may contain directed, bidirected, and undirected edges. An i-minimal
    m-separating set is a minimal m-separator that contains i.

    This implements the m-separation algorithm FINDSEP presented in [1]_ for ancestral mixed
    graphs.  The algorithm has runtime :math:`O(|E| + |V|)` for number of edges :math`|E|` and
    number of vertices :math:`|V|`.

    This implementation differs from the specification of FINDMINSEP in [1]_ in that all
    nodes in ``i`` are removed from the anterior graph :math:`G'`, in between lines 3 and 4.
    This change was deemed necessary because otherwise the TESTSEP call in line 7 would fail
    even if the union of ``z`` and ``i`` was a valid i-minimal m-separating set.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    x : node
        Node in ``G``.
    y : node
        Node in ``G``.
    i : set
        Set of nodes which are always included in the found separating set,
        default is None, which is later set to empty set.
    r : set
        Largest set of nodes which may be included in the found separating set,
        default is None, which is later set to all vertices in ``G``.
    directed_edge_name : str
        Name of the directed edge, default is 'directed'.
    bidirected_edge_name : str
        Name of the bidirected edge, default is 'bidirected'.
    undirected_edge_name : str
        Name of the undirected edge, default is 'undirected'.

    Returns
    -------
    z : set | None
        If a separating set exists, returns a set of nodes which m-separates ``x``
        and ``y``, otherwise returns None.

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.
    """

    if i is None:
        i = set()
    if r is None:
        r = set(G.nodes())
    if not i <= r:
        raise nx.NetworkError(
            f"Minimal set {i} should be no larger than maximal set {r}"
        )

    G_copy = G.copy()

    nodeset = {x, y}.union(i)

    anterior_nodes_G = _anterior(G_copy, nodeset)
    G_copy.remove_nodes_from(set(G_copy.nodes()) - anterior_nodes_G)
    G_p = G_copy.copy()
    aug_G_p = mixed_edge_moral_graph(
        G_copy,
        directed_edge_name=directed_edge_name,
        bidirected_edge_name=bidirected_edge_name,
        undirected_edge_name=undirected_edge_name,
    )
    for node in i:
        aug_G_p.remove_node(node)
    for node in i:
        G_p.remove_node(node)

    z_prime = r.intersection(
        _anterior(G_copy, {x, y}, directed_edge_name, undirected_edge_name)
    ) - {
        x,
        y,
    }

    z_dprime = _bfs_with_marks(aug_G_p, x, z_prime)
    z = _bfs_with_marks(aug_G_p, y, z_dprime)

    if not m_separated(
        G_p, x, y, z, directed_edge_name, bidirected_edge_name, undirected_edge_name
    ):
        return None

    return z.union(i)
