from networkx.algorithms import bipartite
import networkx as nx
from networkx.exception import NetworkXAlgorithmError
from time import time


def old_weighted_projected_graph(B, nodes, ratio=False):
    r"""Returns a weighted projection of B onto one of its node sets.
    The weighted projected graph is the projection of the bipartite
    network B onto the specified nodes with weights representing the
    number of shared neighbors or the ratio between actual shared
    neighbors and possible shared neighbors if ``ratio is True`` [1]_.
    The nodes retain their attributes and are connected in the resulting
    graph if they have an edge to a common node in the original graph.
    Parameters
    ----------
    B : NetworkX graph
        The input graph should be bipartite.
    nodes : list or iterable
        Distinct nodes to project onto (the "bottom" nodes).
    ratio: Bool (default=False)
        If True, edge weight is the ratio between actual shared neighbors
        and maximum possible shared neighbors (i.e., the size of the other
        node set). If False, edges weight is the number of shared neighbors.
    Returns
    -------
    Graph : NetworkX graph
       A graph that is the projection onto the given nodes.
    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> B = nx.path_graph(4)
    >>> G = bipartite.weighted_projected_graph(B, [1, 3])
    >>> list(G)
    [1, 3]
    >>> list(G.edges(data=True))
    [(1, 3, {'weight': 1})]
    >>> G = bipartite.weighted_projected_graph(B, [1, 3], ratio=True)
    >>> list(G.edges(data=True))
    [(1, 3, {'weight': 0.5})]
    Notes
    -----
    No attempt is made to verify that the input graph B is bipartite, or that
    the input nodes are distinct. However, if the length of the input nodes is
    greater than or equal to the nodes in the graph B, an exception is raised.
    If the nodes are not distinct but don't raise this error, the output weights
    will be incorrect.
    The graph and node properties are (shallow) copied to the projected graph.
    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.
    See Also
    --------
    is_bipartite,
    is_bipartite_node_set,
    sets,
    collaboration_weighted_projected_graph,
    overlap_weighted_projected_graph,
    generic_weighted_projected_graph
    projected_graph
    References
    ----------
    .. [1] Borgatti, S.P. and Halgin, D. In press. "Analyzing Affiliation
        Networks". In Carrington, P. and Scott, J. (eds) The Sage Handbook
        of Social Network Analysis. Sage Publications.
    """
    if B.is_directed():
        pred = B.pred
        G = nx.DiGraph()
    else:
        pred = B.adj
        G = nx.Graph()
    G.graph.update(B.graph)
    G.add_nodes_from((n, B.nodes[n]) for n in nodes)
    n_top = len(B) - len(nodes)

    if n_top < 1:
        raise NetworkXAlgorithmError(
            f"the size of the nodes to project onto ({len(nodes)}) is >= the graph size ({len(B)}).\n"
            "They are either not a valid bipartite partition or contain duplicates"
        )

    for u in nodes:
        unbrs = set(B[u])
        nbrs2 = {n for nbr in unbrs for n in B[nbr]} - {u}
        for v in nbrs2:
            vnbrs = set(pred[v])
            common = unbrs & vnbrs
            if not ratio:
                weight = len(common)
            else:
                weight = len(common) / n_top
            G.add_edge(u, v, weight=weight)
    return G


avg_new, avg_old = 0, 0


for i in range(10):
    big_bipartite = bipartite.random_graph(2000, 2000, 0.25)

    start = time()
    proj = bipartite.weighted_projected_graph(
        big_bipartite, nodes=[i for i in range(1000)]
    )
    end = time()

    new_time = end - start

    start = time()
    proj = old_weighted_projected_graph(big_bipartite, nodes=[i for i in range(1000)])
    end = time()

    old_time = end - start
    avg_new += new_time / 10
    avg_old += old_time / 10
    print(f"Running: new {avg_new}, and the old method takes {avg_old}.")


print(
    f"The new method takes {avg_new} on average, and the old method takes {avg_old} on average."
)
