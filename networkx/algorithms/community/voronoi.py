"""Functions for detecting communities based on Voronoi Community Detection
Algorithm"""

import math

import numpy as np

import networkx as nx
from networkx.algorithms.community.quality import modularity
from networkx.utils import not_implemented_for

__all__ = ["voronoi_communities", "voronoi_partitions"]


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_communities(G, weight="weight", mode="strength", resolution=1, eps=1e-8):
    r"""Find the best partition of a graph using the Voronoi Community Detection
    Algorithm.

    Voronoi Community Detection Algorithm is a deterministic method to extract the community
    structure of a network. This is a deterministic method based on modularity optimization. [1]_

    TODO: WRITE HERE ABOUT HOW THE ALGORITHM WORKS, also the big formula for the modularity maxing
    The transformation ensures that tightly-knit
    nodes within the same community are mathematically "closer", while edges acting as
    bridges between communities are "longer".

    As for the minimum distance, we use the shortest edge length. This may be shorter than the shortest
    incident edge of a generator point, but underestimating the minimum distance does not affect
    the radius optimization negatively.

    As a maximum distance, we use the eccentricity of the first generator. If the graph is not
    strongly connected, we consider a _potential_ first generator from each strongly connected
    component and take the maximum eccentricity of these.

    Parameters
    ----------
    G : NetworkX graph
    weight : string, optional (default: "weight")
    mode : {"strength", "flow"}, optional (default: "strength)
        The strategy to transform weights into distances
        - "strength": $1 / (w * d)$ if weights have a strength-like meaning
        - "flow": $log(w) / d$ if weights have an (information) flow-like meaning
    resolution : float, optional (default: 1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities. This corresponds to the
        resolution parameter :math:`\gamma` in the generalized modularity
        formula. See :func:`~networkx.algorithms.community.quality.modularity`.
    eps : float, optional (default: 1e-8)
        Offset value to ensure numerical stability and avoid division by zero.

    Returns
    -------
    list
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`.

    Examples
    -------

    Notes
    -----

    References
    ----------
    ..[1] Molnár, Botond, Ildikó-Beáta Márton, Szabolcs Horvát, and Mária Ercsey-Ravasz.
    "Community detection in directed weighted networks using Voronoi partitioning."_Scientific reports_14,
    no. 1 (2024): 8124. https://doi.org/10.1038/s41598-024-58624-4

    See Also
    --------
    voronoi_partitions
    """

    if G.number_of_edges() == 0:
        return [{n} for n in G]

    if any(d.get(weight, 1.0) <= 0 for _, _, d in G.edges(data=True)):
        raise ValueError(
            "All edge weights must be positive for Voronoi community detection."
        )

    w_max = max(d.get(weight, 1.0) for _, _, d in G.edges(data=True))

    if w_max > 1:
        G_normalized = G.copy()
        for u, v, data in G_normalized.edges(data=True):
            data[weight] = data.get(weight, 1.0) / w_max
    else:
        G_normalized = G

    G_dist = _transform_weights_to_distances(G_normalized, weight=weight, eps=eps)

    all_pairs_distances = dict(nx.all_pairs_dijkstra_path_length(G_dist, weight=weight))

    weighted_densities = _weighted_local_density(G, weight=weight)

    strengths = dict(G.degree(weight=weight))

    if mode == "strength":
        transformed = {node: float(weighted_densities[node]) for node in G.nodes()}
    elif mode == "flow":
        transformed = {
            node: math.log(float(strengths[node]) + eps)
            / (float(weighted_densities[node]) + eps)
            for node in G.nodes()
        }
    else:
        raise ValueError("Invalid mode")

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
        max_r = min_r + 0.25  # Ensure the np.arange loop runs at least once

    max_modularity = -float("inf")
    best_community = []

    last_generators = None

    step_count = 1
    for r in np.arange(min_r, max_r, 0.25):
        generator_points = _choose_generator_points(r, transformed, all_pairs_distances)

        if generator_points == last_generators:
            continue

        print("step", step_count)
        step_count += 1

        print("currently the generator_points:", generator_points)
        print("current cluster count:", len(generator_points))
        print("currently r:", r)
        mode_to_use = "in" if G.is_directed() else "undirected"

        communities = voronoi_partitions(
            G_dist, generator_points, weight, all_pairs_distances, mode_to_use
        )

        current_modularity = modularity(
            G, communities, weight=weight, resolution=resolution
        )

        last_generators = generator_points

        if current_modularity > max_modularity:
            print("new best modularity found:")
            max_modularity = current_modularity
            best_community = communities

        print("current_modularity:", current_modularity)

    print("communities", best_community)
    print("modularity", max_modularity)

    best_community = sorted(best_community, key=lambda c: min(c))

    return best_community


def _transform_weights_to_distances(G, weight="weight", eps=1e-8):
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

    Returns
    -------
    D : NetworkX graph
        A new graph with the `weight` attribute representing topological distance.
    """

    Gu = G.to_undirected(as_view=True)
    undirected_neighbors = {u: set(Gu[u]) for u in Gu.nodes()}

    D = nx.create_empty_copy(G)

    for u, v, data in G.edges(data=True):
        triangles = len(undirected_neighbors[u] & undirected_neighbors[v])
        degree_u = len(undirected_neighbors[u])
        degree_v = len(undirected_neighbors[v])

        min_degree = min(degree_u - 1, degree_v - 1)
        denominator = min_degree if min_degree > 0 else eps
        ecc = (triangles + 1) / denominator

        w = float(data.get(weight, 1.0))
        w_safe = w if w > 0 else eps
        distance = 1.0 / (w_safe * ecc)

        edge_attrs = data.copy()
        edge_attrs[weight] = distance

        D.add_edge(u, v, **edge_attrs)

    return D


def _weighted_local_density(G, weight="weight"):
    """Calculate the weighted local density for each node in the graph.

    The local density is a metric used to identify the centers of communities
    (generator points). It is calculated based on the node's strength and the
    ratio of internal edges within its neighborhood to the total edges connected
    to its neighborhood.

    Parameters
    ----------
    G : NetworkX graph
    weight : string, optional (default: "weight")

    Returns
    -------
    densities : dict
        A dictionary mapping each node to its weighted local density.
    """

    strengths = dict(G.degree(weight=weight))
    densities = {}

    if G.is_directed():
        out_adj = {u: set(G.successors(u)) for u in G.nodes()}
        in_adj = {u: set(G.predecessors(u)) for u in G.nodes()}
    else:
        out_adj = {u: set(G.neighbors(u)) for u in G.nodes()}
        in_adj = out_adj

    for node in G.nodes():
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


def _choose_generator_points(r, weighted_densities, all_pairs_distances):
    """Identify the generator points (community centers) for the Voronoi partitioning.

    A node is selected as a generator point if it is a local maximum. This means that
    it has the highest weighted local density within a local neighborhood of radius
    `r`. Distance calculations are based on the precomputed all-pairs shortest paths.
    Ties in density are broken deterministically by node ID.

    Parameters
    ----------
    r : float
        The radius defining the local neighborhood around a node.
    weighted_densities : dict
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
        weighted_densities.keys(), key=lambda n: (-weighted_densities[n], n)
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
                weighted_densities[node_i] < weighted_densities[node_j]
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
    direction : {"out", "in", "undirected"}
        TODO: explain direction

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


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_partitions(
    G, generator_points, weight="weight", all_pairs_distances=None, direction="out"
):
    r"""Return partitions for each circle with diameter `r` of the Voronoi Community Detection
    Algorithm.

    TODO: WRITE DOWN HOW THE ALGORITHM WORKS

    Parameters
    ----------
    G : NetworkX graph
    generator_points : list
    weight : string, optional (default: "weight")
    all_pairs_distances : optional, if not given then it gets calculated by the algorithm, but it is high cost
    direction : {"out", "in", "undirected"}
        TODO: explain direction

    Returns
    -------
    list
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`.

    Examples
    -------

    Notes
    -----

    See Also
    --------
    voronoi_communities
    networkx.algorithms.voronoi.voronoi_cells
    """

    if direction not in ("in", "out", "undirected"):
        raise ValueError("direction must be 'in', 'out', or 'undirected'")

    generator_points_set = set(generator_points)
    if not generator_points_set.issubset(G):
        raise ValueError("Invalid vertex ID given as Voronoi generator.")

    if all_pairs_distances is not None:
        return _voronoi_cells_from_distances(
            G, generator_points, all_pairs_distances, direction
        )

    if G.is_directed():
        if direction == "in":
            H = nx.reverse_view(G)
        elif direction == "out":
            H = G
        else:
            H = G.to_undirected(as_view=True)
    else:
        H = G

    cells = nx.voronoi_cells(H, generator_points_set, weight=weight)
    return list(cells.values())
