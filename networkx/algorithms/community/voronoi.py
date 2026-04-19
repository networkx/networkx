"""Functions for detecting communities based on Voronoi Community Detection
Algorithm"""

import math

import networkx as nx
from networkx.algorithms.community.quality import modularity
from networkx.utils import not_implemented_for

__all__ = ["voronoi_communities", "voronoi_partitions"]


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_communities(
    G, weight="weight", weight_transform="strength", resolution=1, eps=1e-8
):
    r"""Find the best partition of a graph using the Voronoi Community Detection
    Algorithm.

    Voronoi Community Detection Algorithm is a deterministic method to extract the
    community structure of a network. This is a deterministic method based on modularity
    optimization. [1]_

    The algorithm works in four steps. The first step is to transform the original edge
    weights into topological distances. To ensure tightly-knit nodes within the same
    community are mathematically "closer", while edges acting as bridges between
    communities are "longer", the distance between nodes $u$ and $v$ is calculated
    inversely proportional to their normalized weight $w_{u,v}$ and their edge
    clustering coefficient $C_{u,v}$:

    .. math ::
        l_{u,v} = \frac{1}{w_{u,v} \cdot C_{u,v}}

    Secondly, it calculates a weighted local density $\rho_i$ for every node $i$:

    .. math ::
        \rho_i = s_i \frac{m_i}{m_i + k_i}

    where $s_i$ is the node's strength (weighted degree), $m_i$ is the number of
    internal edges among the neighbors of $i$, and $k_i$ is the number of external edges
    leaving the neighborhood of $i$. This density is then modified according to the
    `weight_transform` strategy to determine the final metric used for selecting
    generator points.

    On the third step, for a given neighborhood radius $r$, the algorithm identifies
    community centers, called "generator points". A node is selected as a generator
    if its transformed density is a strict local maximum within the topological
    distance $r$. Once generators are selected, the graph is partitioned into Voronoi
    cells by assigning every other node to its topologically closest generator point.

    Finally, the algorithm determines a minimum and maximum radius $r$ based on the
    shortest and longest path distances in the graph. It then deterministically scans
    through this range by incrementing $r$ by a fixed step size (0.01). It computes
    the Voronoi partition for each $r$ step and calculates its modularity. The partition
    that maximizes modularity is returned.

    Parameters
    ----------
    G : NetworkX graph
    weight : string, optional (default: "weight")
    weight_transform : {"strength", "flow"} or callable, optional (default: "strength")
        The strategy to transform weights into distances.
        If a string, it must be one of the following:
        - "strength": uses the weighted local density of each node; if weights have a
        strength-like meaning
        - "flow": uses log(strength(node)) / density(node); if weights have an
        (information) flow-like meaning
        If a function, it must have the signature `function(G, node, strengths, node_densities, eps)`
        and return a float representing the transformed local density of the node.
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities.
    eps : float, optional (default: 1e-8)
        Offset value to ensure numerical stability and avoid division by zero.

    Returns
    -------
    list
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`.

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> communities = nx.community.voronoi_communities(G)
    >>> len(communities)
    2
    >>> sorted(len(c) for c in communities)
    [16, 18]

    Notes
    -----
    Unlike stochastic community detection methods (such as the Louvain and Leiden
    algorithms), this method is fully deterministic. The community structure will
    remain exactly the same across multiple executions on the same graph.

    In the event of ties, the algorithm behaves as follows:
        - If multiple nodes have the exact same weighted local density when selecting
        generator points, the tie is broken deterministically by node ID.
        - If a node is at an equal shortest-path distance from multiple generator
        points, it is assigned to the generator with the highest local density.

    References
    ----------
    .. [1] Molnár, Botond, Ildikó-Beáta Márton, Szabolcs Horvát, and Mária Ercsey-Ravasz.
    "Community detection in directed weighted networks using Voronoi partitioning."_Scientific reports_14,
    no. 1 (2024): 8124. https://doi.org/10.1038/s41598-024-58624-4

    See Also
    --------
    voronoi_partitions
    """

    if G.number_of_edges() == 0:
        return [{n} for n in G]

    if any(w <= 0 for _, _, w in G.edges(data=weight, default=1.0)):
        raise nx.NetworkXError("All edge weights must be positive")

    w_max = max(w for _, _, w in G.edges(data=weight, default=1.0))
    weight_key = weight or "weight"

    G_dist = _transform_weights_to_distances(G, weight=weight_key, eps=eps, w_max=w_max)
    all_pairs_distances = dict(
        nx.all_pairs_dijkstra_path_length(G_dist, weight=weight_key)
    )

    strengths = dict(G.degree(weight=weight))
    node_densities = _weighted_local_density(G, strengths)

    if callable(weight_transform):
        transform_function = weight_transform
    elif isinstance(weight_transform, str):
        if weight_transform == "strength":
            transform_function = _strength_transform
        elif weight_transform == "flow":
            transform_function = _flow_transform
        else:
            raise ValueError(
                f"Invalid weight_transform '{weight_transform}' "
                "Expected 'strength', 'flow', or a callable"
            )
    else:
        raise TypeError("weight_transform must be a string or a callable")

    transformed_densities = {
        node: transform_function(G, node, strengths, node_densities, eps) for node in G
    }

    min_r = float("inf")
    max_r = 0

    for source_distances in all_pairs_distances.values():
        for dist in source_distances.values():
            if dist > 0 and dist != float("inf"):
                min_r = min(min_r, dist)
                max_r = max(max_r, dist)

    if min_r == float("inf"):
        min_r = 0.0
    if max_r <= min_r:
        max_r = min_r + 0.25

    max_modularity = -float("inf")
    best_community = []

    last_generators = None

    direction = "in" if G.is_directed() else "out"

    step = 0.01
    r = min_r
    while r < max_r:
        generator_points = _choose_generator_points(
            r, transformed_densities, all_pairs_distances
        )

        if generator_points == last_generators:
            r += step
            continue

        communities = voronoi_partitions(
            G_dist,
            generator_points,
            weight=weight,
            all_pairs_distances=all_pairs_distances,
            direction=direction,
        )

        current_modularity = modularity(
            G, communities, weight=weight, resolution=resolution
        )

        last_generators = generator_points
        r += step

        if current_modularity > max_modularity:
            max_modularity = current_modularity
            best_community = communities

    return best_community


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_partitions(
    G, generator_points, weight="weight", all_pairs_distances=None, direction="out"
):
    r"""Partition the graph into Voronoi cells around a given set of generator points.

    This function assigns every node in the graph to its closest generator point based
    on shortest-path distance, effectively creating a Voronoi diagram on the network.
    Ties are broken deterministically.

    It is used internally by the Voronoi Community Detection Algorithm to evaluate
    different sets of community centers. See :any:`voronoi_communities`.

    Parameters
    ----------
    G : NetworkX graph
    generator_points : list
        A list of node IDs acting as the centers of the Voronoi cells.
    weight : string, optional (default: "weight")
    all_pairs_distances : dict of dicts, optional
        Precomputed shortest path distances between all nodes. If None, distances
        will be calculated internally.
    direction : {"out", "in"}
        Determines the direction of the shortest paths used to assign nodes to
        generators in directed graphs.
        - "out": Node assignment is based on the shortest path from the generator to the node.
        - "in": Node assignment is based on the shortest path from the node to the generator.
        Ignored for undirected graphs.

    Returns
    -------
    list
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`.

    Examples
    --------
    On a path graph, each node is assigned to its nearest generator:

    >>> import networkx as nx
    >>> G = nx.path_graph(6)
    >>> cells = nx.community.voronoi_partitions(G, generator_points=[0, 5])
    >>> sorted(sorted(c) for c in cells)
    [[0, 1, 2], [3, 4, 5]]

    Notes
    -----

    See Also
    --------
    voronoi_communities
    networkx.algorithms.voronoi.voronoi_cells
    """

    if direction not in ("in", "out"):
        raise ValueError("direction must be 'in' or 'out'")

    generator_points_set = set(generator_points)
    if not generator_points_set.issubset(G):
        raise nx.NodeNotFound("Invalid node ID given as Voronoi generator")

    if all_pairs_distances is not None:
        return _voronoi_cells_from_distances(
            G, generator_points, all_pairs_distances, direction
        )

    if G.is_directed() and direction == "in":
        H = nx.reverse_view(G)
    else:
        H = G

    cells = nx.voronoi_cells(H, generator_points_set, weight=weight)
    return list(cells.values())


def _strength_transform(G, node, strengths, node_densities, eps):
    """Default built-in transformation for strength-based edge weights."""
    return float(node_densities[node])


def _flow_transform(G, node, strengths, node_densities, eps):
    """Default built-in transformation for flow-based edge weights."""
    return math.log(float(strengths[node]) + eps) / (float(node_densities[node]) + eps)


def _transform_weights_to_distances(G, weight="weight", eps=1e-8, w_max=1.0):
    r"""Transform graph edge weights into topological distances based on edge clustering.

    This internal helper function creates a new graph where edge weights represent
    distances, inversely proportional to the original edge weight and the
    edge's local clustering coefficient.

    Parameters
    ----------
    G : NetworkX graph
    weight : string, optional (default: "weight")
    eps : float, optional (default: 1e-8)
        Offset value to ensure numerical stability and avoid division by zero.
    w_max : float, optional (default: 1.0)
        Maximum edge weight in the graph, used to normalize weights to (0, 1].

    Returns
    -------
    G_dist : NetworkX graph
        A new graph with the `weight` attribute representing topological distance.
    """

    Gu = G.to_undirected(as_view=True)
    undirected_neighbors = {u: set(Gu[u]) for u in Gu}

    G_dist = nx.create_empty_copy(G)

    for u, v, data in G.edges(data=True):
        triangles = len(undirected_neighbors[u] & undirected_neighbors[v])
        degree_u = len(undirected_neighbors[u])
        degree_v = len(undirected_neighbors[v])

        min_degree = min(degree_u - 1, degree_v - 1)
        denominator = min_degree if min_degree > 0 else eps
        ecc = (triangles + 1) / denominator

        w = float(data.get(weight, 1.0))
        w_norm = w / w_max

        w_safe = w_norm if w_norm > 0 else eps
        distance = 1.0 / (w_safe * ecc)

        edge_attrs = data.copy()
        edge_attrs[weight] = distance

        G_dist.add_edge(u, v, **edge_attrs)

    return G_dist


def _weighted_local_density(G, strengths):
    """Calculate the weighted local density for each node in the graph.

    The local density is a metric used to identify the centers of communities
    (generator points). It is calculated based on the node's strength and the
    ratio of internal edges within its neighborhood to the total edges connected
    to its neighborhood.

    Parameters
    ----------
    G : NetworkX graph
    strengths : dict
        A dictionary mapping each node to its strength (weighted degree).

    Returns
    -------
    densities : dict
        A dictionary mapping each node to its weighted local density.
    """

    densities = {}

    if G.is_directed():
        out_adj = {u: set(G.successors(u)) for u in G}
        in_adj = {u: set(G.predecessors(u)) for u in G}
    else:
        out_adj = {u: set(G.neighbors(u)) for u in G}
        in_adj = out_adj

    for node in G:
        if G.is_directed():
            neighbors = out_adj[node] | in_adj[node]
        else:
            neighbors = out_adj[node]

        # Internal edges among neighbors
        m = sum(1 for v in neighbors if v in out_adj[node])  # node -> v
        m += sum(1 for v in neighbors if v in in_adj[node])  # v -> node
        m += sum(1 for u in neighbors for v in neighbors if u != v and v in out_adj[u])

        # External edges leaving the neighborhood
        if G.is_directed():
            k = sum(
                1
                for u in neighbors
                for v in out_adj[u]
                if v not in neighbors and v != node
            )
            k += sum(
                1
                for u in neighbors
                for v in in_adj[u]
                if v not in neighbors and v != node
            )
        else:
            k = sum(
                1
                for u in neighbors
                for v in out_adj[u]
                if v not in neighbors and v != node
            )

        s = strengths[node]
        densities[node] = s * m / (m + k) if (m + k) > 0 else 0

    return densities


def _choose_generator_points(r, transformed_densities, all_pairs_distances):
    """Identify the generator points (community centers) for the Voronoi partitioning.

    A node is selected as a generator point if it is a local maximum. This means that
    it has the highest weighted local density within a local neighborhood of radius
    `r`. Distance calculations are based on the precomputed all-pairs shortest paths.
    Ties in density are broken deterministically by node ID.

    Parameters
    ----------
    r : float
        The radius defining the local neighborhood around a node.
    transformed_densities : dict
        A dictionary mapping each node to its weighted local density.
    all_pairs_distances : dict of dicts
        Precomputed shortest path distances between all nodes.

    Returns
    -------
    generator_points : list
        A list of node IDs selected as generator points.
    """

    # Sort by descending density, breaking ties by ascending node ID for determinism
    sorted_nodes = sorted(
        transformed_densities.keys(), key=lambda n: (-transformed_densities[n], n)
    )

    generator_points = []
    generator_set = set()

    for node_i in sorted_nodes:
        is_largest = True
        distances_from_node = all_pairs_distances[node_i]

        for node_j, distance in distances_from_node.items():
            if node_j == node_i or distance > r:
                continue

            if (
                transformed_densities[node_i] < transformed_densities[node_j]
                or node_j in generator_set
            ):
                is_largest = False
                break

        if is_largest:
            generator_points.append(node_i)
            generator_set.add(node_i)

    return generator_points


def _voronoi_cells_from_distances(G, generator_points, all_pairs_distances, direction):
    """Helper function to build Voronoi cells using precomputed distances.

    Parameters
    ----------
    G : NetworkX graph
    generator_points : list
    all_pairs_distances : dict
    direction : {"out", "in"}
        Determines the direction of the shortest paths used to assign nodes to
        generators in directed graphs.
        - "out": Node assignment is based on the shortest path from the generator to the node.
        - "in": Node assignment is based on the shortest path from the node to the generator.
        Ignored for undirected graphs.

    Returns
    -------
    list of sets
        A list of disjoint sets representing the partitioned communities.
    """

    cell_dict = {g: set() for g in generator_points}
    unreachable = set()

    if direction == "in":
        for node in G:
            node_distances = all_pairs_distances.get(node, {})
            best_generator = None
            best_distance = float("inf")

            for g in generator_points:
                d = node_distances.get(g, float("inf"))
                if d < best_distance:
                    best_distance = d
                    best_generator = g

            if best_generator is not None:
                cell_dict[best_generator].add(node)
            else:
                unreachable.add(node)

    else:
        generator_distances = {
            g: all_pairs_distances.get(g, {}) for g in generator_points
        }
        for node in G:
            best_generator = None
            best_distance = float("inf")

            for g in generator_points:
                d = generator_distances[g].get(node, float("inf"))
                if d < best_distance:
                    best_distance = d
                    best_generator = g

            if best_generator is not None:
                cell_dict[best_generator].add(node)
            else:
                unreachable.add(node)

    cells = [group for group in cell_dict.values() if group]

    if unreachable:
        cells.append(unreachable)

    return cells
