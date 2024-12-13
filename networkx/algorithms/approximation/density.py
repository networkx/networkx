"""Fast algorithms for the densest subgraph problem"""

import networkx as nx

__all__ = ["densest_subgraph"]


def _greedy_plus_plus(G, iterations):
    if G.number_of_edges() == 0:
        return 0.0, set()
    if iterations < 1:
        raise ValueError(
            f"The number of iterations must be an integer >= 1. Provided: {iterations}"
        )

    loads = {node: 0 for node in G.nodes}  # Load vector for Greedy++.
    best_density = 0.0  # Highest density encountered.
    best_subgraph = set()  # Nodes of the best subgraph found.

    for _ in range(iterations):
        # Initialize heap for fast access to minimum weighted degree.
        heap = nx.utils.BinaryHeap()

        # Compute initial weighted degrees and add nodes to the heap.
        for node, degree in G.degree:
            heap.insert(node, loads[node] + degree)

        # Set up tracking for current graph state.
        remaining_nodes = set(G.nodes)
        num_edges = G.number_of_edges()
        current_degrees = dict(G.degree)

        while remaining_nodes:
            num_nodes = len(remaining_nodes)

            # Current density of the (implicit) graph
            current_density = num_edges / num_nodes

            # Update the best density.
            if current_density > best_density:
                best_density = current_density
                best_subgraph = set(remaining_nodes)

            # Pop the node with the smallest weighted degree.
            node, _ = heap.pop()
            if node not in remaining_nodes:
                continue  # Skip nodes already removed.

            # Update the load of the popped node.
            loads[node] += current_degrees[node]

            # Update neighbors' degrees and the heap.
            for neighbor in G.neighbors(node):
                if neighbor in remaining_nodes:
                    current_degrees[neighbor] -= 1
                    num_edges -= 1
                    heap.insert(neighbor, loads[neighbor] + current_degrees[neighbor])

            # Remove the node from the remaining nodes.
            remaining_nodes.remove(node)

    return best_density, best_subgraph


ALGORITHMS = {"greedy++": _greedy_plus_plus}


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable
def densest_subgraph(G, iterations=1, *, method="greedy++"):
    r"""Returns an approximate densest subgraph for a graph `G`.

    This function runs an iterative algorithm to find the densest subgraph, and
    returns both the density and the subgraph. For a discussion on the notion of
    density used and the different algorithms available on networkx, please see
    the Notes section below.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph.

    iterations : int, optional (default=1)
        Number of iterations to use for the iterative algorithm. Can be specified
        positionally or as a keyword argument.

    method : string, optional (default='greedy++')
        The algorithm to use to approximate the densest subgraph.
        Supported options: 'greedy++'.
        Must be specified as a keyword argument. Other inputs produce a ValueError.

    Returns
    -------
    d : float
        The density of the approximate subgraph found.

    S : set
        The subset of nodes defining the approximate densest subgraph.

    Examples
    --------
    >>> G = nx.star_graph(4)
    >>> nx.approximation.densest_subgraph(G, iterations=1)
    (0.8, {0, 1, 2, 3, 4})

    Notes
    -----
    The densest subgraph problem (DSG) asks to find the subgraph $S \subseteq V(G)$
    with maximum density. For a subset of the nodes of $G$, $S \subseteq V(G)$,
    define $E(S) = \{ (u,v) : (u,v)\in E(G), u\in S, v\in S \}$ as the set of
    edges with both endpoints in $S$. The density of $S$ is defined as $|E(S)|/|S|$,
    the ratio between the edges in the subgraph $G[S]$ and the number of nodes in
    that subgraph. Note that this is different from the standard graph theoretic
    definition of density, defined as $\frac{2|E(S)|}{|S|(|S|-1)}$, for historical
    reasons.

    The densest subgraph problem is polynomial time solvable using maximum flow,
    commonly refered to as Goldberg's algorithm. However, the algorithm is quite
    involved. It first binary searches on the optimal density, $d^\ast$. For a
    guess of the density $d$, it sets up a flow network $G'$ with size O(m). The
    maximum flow solution either informs the algorithm that no subgraph with
    density $d$ exists, or it provides a subgraph with density at least $d$.
    However, this is inherently bottlenecked by the maximum flow algorithm. For
    example, [2]_ notes that Goldberg’s algorithm was not feasible on many large
    graphs even though they used a highly optimized maximum flow library.

    While exact solution algorithms are quite involved, there are several known
    approximation algorithms for the densest subgraph problem.

    Charikar [1]_ described a very simple 1/2-approximation algorithm for DSG
    known as the greedy "peeling" algorithm. The algorithm creates an ordering of
    the nodes as follows. The first node $v_1$ is the one with the smallest degree
    in $G$ (ties broken arbitrarily). It selects $v_2$ to be the smallest degree
    node in $G \setminus v_1$. Letting $G_i$ be the graph after removing
    $v_1, ..., v_i$ (with $G_0=G$), the algorithm returns the graph among
    $G_0, ..., G_n$ with the highest density.

    Boob et al. [2]_ generalized this algorithm into Greedy++, an iterative
    algorithm that runs several rounds of "peeling". In fact, Greedy++ with 1
    iteration is precisely Charikar's algorithm. The algorithm converges to a
    $(1-\epsilon)$ approximate densest subgraph in $O(\Delta(G)\log n/\epsilon^2)$
    iterations, where $\Delta(G)$ is the maximum degree, and $n$ is number of
    nodes in $G$. The algorithm also has other desirable properties as shown by
    [4]_ and [5]_.

    Harb et al. [3]_ gave a faster and more scalable algorithm using ideas from
    quadratic programming for the densest subgraph, which is based on a fast
    iterative shrinkage-thresholding algorithm (FISTA) algorithm.

    References
    ----------
    .. [1] Charikar, Moses. "Greedy approximation algorithms for finding dense
    components in a graph." In International workshop on approximation
    algorithms for combinatorial optimization, pp. 84-95. Berlin, Heidelberg:
    Springer Berlin Heidelberg, 2000.

    .. [2] Boob, Digvijay, Yu Gao, Richard Peng, Saurabh Sawlani, Charalampos
    Tsourakakis, Di Wang, and Junxing Wang. "Flowless: Extracting densest
    subgraphs without flow computations." In Proceedings of The Web Conference
    2020, pp. 573-583. 2020.

    .. [3] Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri. "Faster and scalable
    algorithms for densest subgraph and decomposition." Advances in Neural
    Information Processing Systems 35 (2022): 26966-26979.

    .. [4] Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri. "Convergence to
    lexicographically optimal base in a (contra) polymatroid and applications
    to densest subgraph and tree packing." arXiv preprint arXiv:2305.02987
    (2023).

    .. [5] Chekuri, Chandra, Kent Quanrud, and Manuel R. Torres. "Densest
    subgraph: Supermodularity, iterative peeling, and flow." In Proceedings of
    the 2022 Annual ACM-SIAM Symposium on Discrete Algorithms (SODA), pp.
    1531-1555. Society for Industrial and Applied Mathematics, 2022.
    """
    try:
        algo = ALGORITHMS[method]
    except KeyError as e:
        raise ValueError(f"{method} is not a valid choice for an algorithm.") from e

    return algo(G, iterations)
