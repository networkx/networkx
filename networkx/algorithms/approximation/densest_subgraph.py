"""Fast algorithms for densest subgraph problem"""

import networkx as nx

__all__ = ["greedy_plus_plus"]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable
def greedy_plus_plus(G, iterations):
    r"""Returns an approximate densest subgraph for a graph `G`.

    This function runs Boob et al. [2]_ Greedy++ algorithm to find
    the densest subgraph, and returns both the density and the subgraph.
    For a discussion on the notion of density used and the different
    algorithms available on networkx, please see the Notes section below.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    iterations: int
        Number of iterations to use for the Greedy++ algorithm. ``iterations=1``
        is equivalent to the greedy "peeling" algorithm in [1]_.

    Returns
    -------
    d : float
        The density of the approximate subgraph found.

    S : set
        The subset of nodes defining the approximate densest subgraph.

    Examples
    --------
    >>> G = nx.star_graph(4)
    >>> nx.approximation.greedy_plus_plus(G, iterations=1)
    (0.8, {0, 1, 2, 3, 4})

    Notes
    -----
    For a subset of the nodes of $G$, $S \subseteq V(G)$, define
    $E(S) = \{ (u,v) : (u,v)\in E(G), u\in S, v\in S \}$ as the set of
    edges with both endpoints in $S$. The density of $S$ is defined as
    $E(S)/|S|$, the ratio between the edges in the subgraph $G[S]$ and
    the number of nodes in that subgraph. The densest subgraph problem
    asks to find the subgraph $S \subseteq V(G)$ with maximum density.

    The densest subgraph problem is polynomial time solvable using
    maximum flow, commonly refered to as Goldberg's algorithm.
    However, the algorithm is quite involved. It first
    binary searches on the optimal density, $d^\ast$. For a guess of
    the density $d$, it sets up a flow network $G'$ with size O(m). The
    maximum flow solution either informs the algorithm that no subgraph
    with density $d$ exists, or it returns (implicitly) a subgraph with density
    $d$. However, this is inherently bottlenecked by the maximum flow algorithm.
    For example, authors from [2]_ noted that Goldberg’s algorithm
    failed on many large graphs even though they used a highly optimized
    maximum flow library.

    Due to the importance of the problem and solving it on large scale graphs,
    there are several known approximation algorithms for the problem.

    Charikar [1]_ described a very simple 1/2-approximation algorithm for DSG known as
    the greedy "peeling" algorithm. The algorithm creates an ordering of the nodes as follows.
    The first node $v_1$ is the one with the smallest degree in $G$ (ties broken arbitrarily).
    It selects $v_2$ to be the smallest degree node in $G \setminus v_1$. Letting $G_i$ be the
    graph after removing $v_1, ..., v_i$ (with $G_0=G$), the algorithm returns the graph among
    $G_0, ..., G_n$ with the highest density.

    Boob et al. [2]_ generalized this algorithm into Greedy++, an iterative algorithm that runs
    several rounds of "peeling". In fact, Greedy++ with 1 iteration is precisely Charikar's algorithm.
    The algorithm converges to a $(1-\epsilon)$ approximate densest
    subgraph in $O(\Delta(G)\log n/\epsilon^2)$ iterations, and has other desirable properties as shown by
    [4]_ and [5]_.

    Harb et al. [3]_ gave a faster and more scalable algorithm using ideas from quadratic programming
    for the densest subgraph, which is based on FISTA algorithm.

    References
    ----------
    .. [1] Charikar, Moses. "Greedy approximation algorithms for finding dense components in a graph."
        In International workshop on approximation algorithms for combinatorial optimization, pp. 84-95.
        Berlin, Heidelberg: Springer Berlin Heidelberg, 2000.

    .. [2] Boob, Digvijay, Yu Gao, Richard Peng, Saurabh Sawlani, Charalampos Tsourakakis, Di Wang,
        and Junxing Wang. "Flowless: Extracting densest subgraphs without flow computations."
        In Proceedings of The Web Conference 2020, pp. 573-583. 2020.

    .. [3] Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri.
        "Faster and scalable algorithms for densest subgraph and decomposition."
        Advances in Neural Information Processing Systems 35 (2022): 26966-26979.

    .. [4] Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri.
        "Convergence to lexicographically optimal base in a (contra) polymatroid and applications to
        densest subgraph and tree packing." arXiv preprint arXiv:2305.02987 (2023).

    .. [5] Chekuri, Chandra, Kent Quanrud, and Manuel R. Torres. "Densest subgraph: Supermodularity,
        iterative peeling, and flow."
        In Proceedings of the 2022 Annual ACM-SIAM Symposium on Discrete Algorithms (SODA), pp. 1531-1555.
        Society for Industrial and Applied Mathematics, 2022.
    """
    if G.number_of_edges() == 0:
        return 0.0, set()
    if iterations < 1:
        raise ValueError(
            f"The number of iterations must be an integer at least 1. Provided value is {iterations}"
        )

    loads = {u: 0 for u in G.nodes}  # The load vector for Greedy++.
    best_density = 0.0  # Best density found so far.
    best_subgraph = set()  # Best subgraph found so far.

    for _ in range(iterations):
        # Initialize the heap for fast minimum degree
        heap = nx.utils.BinaryHeap()

        # Calculate the current weighted degrees (load + degree of node) and add it to the heap.
        weighted_degrees = {u: loads[u] + d for u, d in G.degree()}
        for u in G.nodes:
            heap.insert(u, weighted_degrees[u])

        # Copy the graph structure for this iteration
        G_iter = G.copy()

        while G_iter.number_of_nodes() >= 1:
            current_density = (
                G_iter.number_of_edges() / G_iter.number_of_nodes()
            )  # Current density of G_iter

            if current_density > best_density:
                best_density = current_density
                best_subgraph = set(G_iter.nodes)

            u, _ = heap.pop()  # Pick node with minimum current weighted degree

            loads[u] += G_iter.degree[u]  # Add to load of u

            # Subtract one edge from all of u's neighbors, and update their weighted degree
            for v in G_iter.neighbors(u):
                weighted_degrees[v] -= 1
                heap.insert(v, weighted_degrees[v])

            # Delete u
            G_iter.remove_node(u)

    return (best_density, best_subgraph)
