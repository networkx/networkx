"""Functions for detecting communities based on Voronoi Community Detection
Algorithm"""

import math

import numpy as np

import networkx as nx
from networkx.algorithms.community.quality import modularity
from networkx.utils import not_implemented_for

__all__ = ["voronoi_communities", "voronoi_partitions"]

# function dictionary, if there is a 3rd word that doesnt match the first 2 then wait for user defined
# give function by param

# optional param, how many clusters do you want?
# optional param, we can also maximize other functions not just modularity


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_communities(G, weight="weight", mode="strength", eps=1e-8):
    r"""Find the best partition of a graph using the Voronoi Community Detection
    Algorithm.

    Voronoi Community Detection Algorithm is a deterministic method to extract the community
    structure of a network. This is a deterministic method based on modularity optimization. [1]_

    TODO: WRITE HERE ABOUT HOW THE ALGORITHM WORKS, also the big formula for the modularity maxing
    The transformation ensures that tightly-knit
    nodes within the same community are mathematically "closer", while edges acting as
    bridges between communities are "longer".

    Parameters
    ----------
    G : NetworkX graph
    weight : string, optional (default: "weight")
    mode : {"strength", "flow"}, optional (default: "strength)
        The strategy to transform weights into distances
        - "strength": $1 / (w * d)$ if weights have a strength-like meaning
        - "flow": $log(w) / d$ if weights have an (information) flow-like meaning
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
    .. [1] Molnár, Botond, Ildikó-Beáta Márton, Szabolcs Horvát, and Mária Ercsey-Ravasz.
    "Community detection in directed weighted networks using Voronoi partitioning."_Scientific reports_14,
    no. 1 (2024): 8124. https://doi.org/10.1038/s41598-024-58624-4

    See Also
    --------
    voronoi_partitions
    :any:`voronoi_communities`
    """

    if G.number_of_edges() == 0:
        return [{n} for n in G]

    G_dist = _transform_weights_to_distances(G, weight=weight, eps=eps)

    all_pairs_distances = dict(nx.all_pairs_dijkstra_path_length(G_dist, weight=weight))

    # check if any weight is 0, return with exception

    weighted_densities = _weighted_local_density(G, weight=weight)

    nodes = list(G.nodes())
    # does this G.degree weight exist if it is unweighted
    strengths = dict(G.degree(weight=weight))

    # DATA HAS TO BE NORMALIZED, if >1 i need to normalize
    if mode == "strength":
        transformed = {node: float(weighted_densities[node]) for node in nodes}
    elif mode == "flow":
        transformed = {
            node: math.log(float(strengths[node]) + eps)
            / (float(weighted_densities[node]) + eps)
            for node in nodes
        }
    else:
        raise ValueError("Invalid mode")

    # As for the minimum distance, we use the shortest edge length. This may be shorter than the shortest
    # incident edge of a generator point, but underestimating the minimum distance does not affect
    # the radius optimization negatively.

    # min_r -> shortest dijkstra path length
    min_r = float("inf")
    for source_distances in all_pairs_distances.values():
        for dist in source_distances.values():
            if dist > 0:  # Exclude distance to self (which is 0)
                min_r = min(min_r, dist)

    # As a maximum distance, we use the eccentricity of the first generator. If the graph is not
    # strongly connected, we consider a _potential_ first generator from each strongly connected
    # component and take the maximum eccentricity of these. */

    max_r = 0
    if G_dist.is_directed():
        components = nx.strongly_connected_components(G_dist)
    else:
        components = nx.connected_components(G_dist)

    for component in components:
        subgraph = G_dist.subgraph(component)
        ecc_dict = nx.eccentricity(subgraph)
        max_r = max(max_r, max(ecc_dict.values()))
    max_r *= 2

    max_modularity = -float("inf")
    best_community = {}

    step_count = 1
    for r in np.arange(
        min_r, max_r, 0.25
    ):  # normal python range does not allow float steps
        print("step", step_count)
        step_count += 1

        generator_points = _choose_generator_points(r, transformed, all_pairs_distances)
        print("currently the generator_points:", generator_points)
        print("current cluster count:", len(generator_points))
        print("currently r:", r)
        mode_to_use = "in" if G.is_directed() else "undirected"
        voronoi_community = voronoi_partitions(
            G_dist, generator_points, weight, all_pairs_distances, mode_to_use
        )

        groups = {}
        for node, community_id in voronoi_community.items():
            if community_id not in groups:
                groups[community_id] = set()
            groups[community_id].add(node)

        current_modularity = modularity(G, list(groups.values()))

        if current_modularity > max_modularity:
            print("new best modularity found:")
            max_modularity = current_modularity
            best_community = voronoi_community

        print("current_modularity:", current_modularity)

    print("communities", best_community)
    print("modularity", max_modularity)

    # CREATE FINAL PARTITIONS HERE
    community_mapping = {}
    for node, community_id in best_community.items():
        if community_id not in community_mapping:
            community_mapping[community_id] = set()
        community_mapping[community_id].add(node)

    # Convert to a list of sets
    final_partition = list(community_mapping.values())

    return final_partition


def _transform_weights_to_distances(G, weight="weight", eps=1e-8):
    r"""Transform graph edge weights into topological distances based on edge clustering.

    This internal helper function creates a new graph where edge weights represent
    distances, inversely proportional to the original edge weight and the
    edge's local clustering coefficient.

    TODO: formula?

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

    TODO: formula?

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


# add param: how many communities we want to have,
# clarify


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_partitions(
    G, generator_points, weight="weight", all_pairs_distances=None, mode="out"
):
    r"""Yield partitions for each circle with diameter `r` of the Voronoi Community Detection
    Algorithm.

    TODO: WRITE DOWN HOW THE ALGORITHM WORKS

    Parameters
    ----------
    G : NetworkX graph
    generator_points : list
    weight : string, optional (default: "weight")
    all_pairs_distances : optional, if not given then it gets calculated by the algorithm, but it is high cost
    mode : {"out", "in", "undirected"}

    Yields
    ------
    list
        A list of disjoint sets (partition of `G`). Each set represents one community.
        All communities together contain all the nodes in `G`.

    References
    ----------

    See Also
    --------
    voronoi_communities
    :any:`voronoi_partitions`
    """

    # if directed, we need to know if we are measuring distance from generators outward
    # or to generators inward or ignoring the direction
    if mode not in ("in", "out", "undirected"):
        raise ValueError("mode must be 'in', 'out', or 'undirected'")

    # validating that all generators exist in the graph
    if not all(g in G.nodes for g in generator_points):
        raise ValueError("Invalid vertex ID given as Voronoi generator.")

    if G.is_directed():
        if mode == "in":
            G_use = G.reverse()
        elif mode == "out":
            G_use = G
        else:
            G_use = G.to_undirected()
    else:
        G_use = G

    membership = {node: -1 for node in G_use.nodes()}

    # If precomputed distances provided, use them
    # In the precomputed branch, the lookup all_pairs_distances[node][generator]
    # already encodes dist(node -> generator); mode is not applied here.
    if all_pairs_distances is not None:
        for node in G_use.nodes():
            min_distance = float("inf")
            closest_generator_idx = -1

            for generator_idx, generator in enumerate(generator_points):
                # Look up precomputed distance
                if (
                    node in all_pairs_distances
                    and generator in all_pairs_distances[node]
                ):
                    distance = all_pairs_distances[node][generator]

                    if distance < min_distance:
                        min_distance = distance
                        closest_generator_idx = generator_idx

            membership[node] = closest_generator_idx

    else:
        # Original implementation: compute on-demand
        reachable_from = {node: [] for node in G_use.nodes()}

        for generator_index, generator in enumerate(generator_points):
            if nx.is_weighted(G_use):
                lengths = nx.single_source_dijkstra_path_length(
                    G_use, generator, weight=weight
                )
            else:
                lengths = nx.single_source_shortest_path_length(G_use, generator)

            for node, distance in lengths.items():
                reachable_from[node].append((generator_index, distance))

        for node in G_use.nodes():
            if not reachable_from[node]:
                continue

            minimum_distance = min(distance for _, distance in reachable_from[node])

            closest_generators = [
                generator_index
                for generator_index, distance in reachable_from[node]
                if distance == minimum_distance
            ]

            membership[node] = closest_generators[0]

    # TODO: YIELD!!!
    return membership
