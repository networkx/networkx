from networkx.algorithms.mis import maximal_independent_set

__all__ = ["sampled_rlf_color"]


def sampled_rlf_color(G, n_searches=1_000):
    """Color a graph using variant of Recursive Largest First algorithm.

    Attempts to color a graph using as few colors as possible, where no
    neighbors of a node can have same color as the node itself. At each
    stage a maximal independent set of nodes is colored with a previously
    unused color. The maximal independent set is found using `n_searches`
    attempts with a greedy random maximal independent set algorithm.
    The maximal independent set with the greatest number of nodes is
    selected to be colored. The pseudo-code for this algorithm is as follows:

    1. Let `G` be an undirected graph.
    2. Select an arbitrary node with the highest degree.
    3. Sample `n_searches` maximal independent sets using
    `nx.maximal_independent_set()` starting from that node
    and choose the set with the greatest number of nodes.
    4. Assign all nodes in the chosen set to a previously unused color.
    5. Remove those nodes from the graph.
    6. Repeat steps 2 through 5 until there are no more nodes
    in the graph.

    Parameters
    ----------
    G : NetworkX graph

    n_searches : int
       the number of maximal independent set samples to take
       from graph G. Default is 1,000.

    Returns
    -------
    A dictionary with keys representing nodes and values representing
    corresponding coloring.

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (1, 2), (1, 3)])
    >>> d = nx.coloring.sampled_rlf_color(G, n_searches=1_000)
    >>> d == {0: 1, 1: 0, 2: 1, 3: 1}
    True

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed.

    References
    ----------
    .. [1] 'Recursive Largest First Algorithm.'
       Wikipedia. Wikimedia Foundation, January 15, 2022.
       https://en.wikipedia.org/wiki/Recursive_largest_first_algorithm#cite_ref-:1_2-0.
    """
    color = {}

    temp_graph = G.copy()
    color_iter = 0

    while len(temp_graph.nodes) > 0:
        # finding node with the highest degree
        init_node = max(temp_graph.degree, key=lambda x: x[1])[0]

        # iteratively finding maximal independent set, assigning color
        # then removing the maximal independent set from the graph
        max_len = 0
        iteration = 0
        while iteration < n_searches:
            indep_nodes = maximal_independent_set(
                temp_graph, nodes=[init_node], seed=None
            )
            if len(indep_nodes) > max_len:
                max_independent_set = indep_nodes
                max_len = len(indep_nodes)
            iteration += 1

        for node in max_independent_set:
            color[node] = color_iter

        color_iter += 1
        temp_graph.remove_nodes_from(max_independent_set)

    return color
