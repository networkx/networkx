"""Fast algorithms for the densest subgraph problem"""

import math

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


# Generator for edges in both directions for an undirected graph
def _bidirectional_edges(G):
    for u, v in G.edges():
        yield (u, v)
        yield (v, u)


def _fractional_peeling(G, b, x, node_to_idx, idx_to_node, edge_to_idx, idx_to_edge):
    """
    Optimized fractional peeling using NumPy arrays.

    Parameters:
        G (networkx.Graph): The input graph.
        b (numpy.ndarray): Induced load vector.
        x (numpy.ndarray): Fractional edge values.
        node_to_idx (dict): Mapping from node to index.
        idx_to_node (dict): Mapping from index to node.
        edge_to_idx (dict): Mapping from edge to index.
        idx_to_edge (dict): Mapping from index to edge.

    Returns:
        best_density (float): The best density found.
        best_subgraph (set): The subset of nodes defining the densest subgraph.
    """
    heap = nx.utils.BinaryHeap()
    # Initialize heap with b values
    for idx, node in enumerate(G.nodes()):
        heap.insert(idx, b[idx])

    remaining_nodes = set(range(len(G.nodes())))
    num_edges = G.number_of_edges()

    best_density = 0.0
    best_subgraph = set()

    while remaining_nodes:
        num_nodes = len(remaining_nodes)
        current_density = num_edges / num_nodes

        if current_density > best_density:
            best_density = current_density
            best_subgraph = {idx_to_node[idx] for idx in remaining_nodes}

        # Pop the node with the smallest b
        node_idx, _ = heap.pop()
        while node_idx not in remaining_nodes:
            node_idx, _ = heap.pop()  # Clean the heap from stale values

        # Update neighbors
        for neighbor in G.neighbors(idx_to_node[node_idx]):
            neighbor_idx = node_to_idx[neighbor]
            if neighbor_idx in remaining_nodes:
                # Find edge index
                edge = (idx_to_node[node_idx], neighbor)
                edge_idx = edge_to_idx.get(edge)
                if edge_idx is not None:
                    b[neighbor_idx] -= x[edge_idx]
                    num_edges -= 1
                    heap.insert(neighbor_idx, b[neighbor_idx])

        remaining_nodes.remove(node_idx)

    return best_density, best_subgraph


def _fista(G, iterations):
    if G.number_of_edges() == 0:
        return 0.0, set()
    if iterations < 1:
        raise ValueError(
            f"The number of iterations must be an integer >= 1. Provided: {iterations}"
        )
    import numpy as np

    # 1. Node Mapping: Assign a unique index to each node
    node_list = list(G.nodes)
    node_to_idx = {node: idx for idx, node in enumerate(node_list)}
    idx_to_node = {idx: node for node, idx in node_to_idx.items()}
    num_nodes = len(node_list)

    # 2. Edge Mapping: Assign a unique index to each bidirectional edge
    bidirectional_edges = list(_bidirectional_edges(G))
    num_edges = len(bidirectional_edges)
    edge_to_idx = {edge: idx for idx, edge in enumerate(bidirectional_edges)}
    idx_to_edge = {idx: edge for edge, idx in edge_to_idx.items()}

    # 3. Reverse Edge Mapping: Map each edge to its reverse edge index
    reverse_edge_idx = np.empty(num_edges, dtype=np.int32)
    for idx, (u, v) in enumerate(bidirectional_edges):
        reverse_edge_idx[idx] = edge_to_idx[(v, u)]

    # 4. Initialize Variables as NumPy Arrays
    x = np.full(num_edges, 0.5, dtype=np.float32)
    last_x = x.copy()
    y = x.copy()
    z = np.zeros(num_edges, dtype=np.float32)
    b = np.zeros(num_nodes, dtype=np.float32)  # Induced load vector
    tk = 1.0  # Momentum term

    # 5. Precompute Edge Source Indices
    edge_src_indices = np.array(
        [node_to_idx[u] for u, _ in bidirectional_edges], dtype=np.int32
    )

    # 6. Compute Learning Rate
    max_degree = max(dict(G.degree()).values())
    learning_rate = 0.9 / max_degree

    # 7. Iterative Updates
    for _ in range(iterations):
        # 7a. Update b: sum y over outgoing edges for each node
        b[:] = 0.0  # Reset b to zero
        np.add.at(b, edge_src_indices, y)

        # 7b. Compute z
        z = y - 2.0 * learning_rate * b[edge_src_indices]

        # 7c. Update Momentum Term
        tknew = (1.0 + math.sqrt(1 + 4.0 * tk**2)) / 2.0

        # 7d. Update x, y, and last_x in a vectorized manner
        new_xuv = (z - z[reverse_edge_idx] + 1.0) / 2.0
        clamped_x = np.clip(new_xuv, 0.0, 1.0)

        # Update y using the FISTA update rule
        y = (
            clamped_x
            + ((tk - 1.0) / tknew) * (clamped_x - last_x)
            + (tk / tknew) * (clamped_x - y)
        )

        # Update x and last_x
        last_x = x.copy()
        x = clamped_x

        # Update tk, the momemntum term
        tk = tknew

    return _fractional_peeling(
        G, b, x, node_to_idx, idx_to_node, edge_to_idx, idx_to_edge
    )


ALGORITHMS = {"greedy++": _greedy_plus_plus, "fista": _fista}


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable
def densest_subgraph(G, iterations=1, *, method="fista"):
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

    method : string, optional (default='fista')
        The algorithm to use to approximate the densest subgraph.
        Supported options: 'greedy++' by Boob et al. [2]_ and 'fista' by Harb et al. [3]_.
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
