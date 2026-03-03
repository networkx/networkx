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
def voronoi_communities(G, mode="strength", eps=1e-8):
    r"""Find the best partition of a graph using the Voronoi Community Detection
    Algorithm.

    Voronoi Community Detection Algorithm is a deterministic method to extract the community
    structure of a network. This is a deterministic method based on modularity optimization. [1]_

    TODO: WRITE HERE ABOUT HOW THE ALGORITHM WORKS, also the big formula for the modularity maxing

    Parameters
    ----------
    G : NetworkX graph
    mode : {"strength", "flow"}, optional (default: "strength)
        The strategy to transform weights into distances
        - "strength": $1 / (w * d)$ if weights have a strength-like meaning
        - "flow": $log(w) / d$ if weights have an (information) flow-like meaning
    eps : float, optional (default: 1e-8)
        Small offset value added to denominators and logarithms to
        ensure numerical stability and avoid division by zero.

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

    G_dist = _transform_weights_to_distances(G)

    all_pairs_distances = dict(
        nx.all_pairs_dijkstra_path_length(G_dist, weight="weight")
    )

    # check if any weight is 0, return with exception

    weighted_densities = _weighted_local_density(G)

    nodes = list(G.nodes())
    # does this G.degree weight exist if it is unweighted
    strengths = dict(G.degree(weight="weight"))

    # DATA HAS TO BE NORMALIZED, if >1 i need to normalize
    if mode == "strength":
        transformed = {
            node: float(strengths[node]) * float(weighted_densities[node])
            for node in nodes
        }
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

        generator_points = _choose_generator_points(
            G_dist, r, transformed, all_pairs_distances
        )
        print("currently the generator_points:", generator_points)
        print("current cluster count:", len(generator_points))
        print("currently r:", r)
        mode_to_use = "out" if G.is_directed() else "undirected"
        voronoi_community = voronoi_partitions(
            G_dist, generator_points, all_pairs_distances, mode_to_use
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


def _transform_weights_to_distances(G):
    EPS = 1e-8

    Gu = G.to_undirected()
    neighbors = {u: set(Gu[u]) for u in Gu.nodes()}

    if G.is_directed():
        D = nx.DiGraph()
    else:
        D = nx.Graph()

    D.add_nodes_from(G.nodes())

    for edge_count, (u, v, data) in enumerate(G.edges(data=True), 1):
        # triangle count for this edge
        t = len(neighbors[u] & neighbors[v])

        deg_u = len(neighbors[u])
        deg_v = len(neighbors[v])
        min_deg = min(deg_u - 1, deg_v - 1)

        if min_deg <= 0:
            ecc = (t + 1) / EPS
        else:
            ecc = (t + 1) / min_deg

        w = float(data.get("weight", 1.0))
        dist = 1.0 / ((w if w > 0 else EPS) * ecc)
        D.add_edge(u, v, weight=dist)

    return D


def _weighted_local_density(G):
    strengths = dict(G.degree(weight="weight"))
    dens = {}

    # adjacency sets for speed (directed)
    # Check if the graph is directed to use successors/predecessors
    # If undirected, neighbors() covers both.
    if G.is_directed():
        out_adj = {u: set(G.successors(u)) for u in G.nodes()}
        in_adj = {u: set(G.predecessors(u)) for u in G.nodes()}
    else:
        # For undirected, successors and predecessors are just neighbors
        out_adj = {u: set(G.neighbors(u)) for u in G.nodes()}
        in_adj = out_adj

    for node in G.nodes():
        # first-order neighborhood: incoming + outgoing neighbors
        neigh = out_adj[node] | in_adj[node]

        # -------------------------
        # 1. INTERNAL m (directed)
        # -------------------------
        m = 0

        # edges between node ↔ neighbors
        for v in neigh:
            if v in out_adj[node]:
                m += 1  # node → v
            if v in in_adj[node]:
                m += 1  # v → node

        # edges among neighbors (directed)
        neigh_list = list(neigh)
        for u in neigh_list:
            for v in neigh_list:
                if u == v:
                    continue
                if v in out_adj[u]:  # u → v
                    m += 1

        # -------------------------
        # 2. EXTERNAL k (directed)
        # -------------------------
        k = 0
        for u in neigh:
            # outgoing from u to outside
            for v in out_adj[u]:
                if v not in neigh and v != node:
                    k += 1

            # incoming to u from outside
            for v in in_adj[u]:
                if v not in neigh and v != node:
                    k += 1

        # -------------------------
        # 3. Compute density
        # -------------------------
        s = strengths[node]
        density = s * m / (m + k) if (m + k) > 0 else 0
        dens[node] = density

    return dens


def _edge_clustering_coefficient(G, u, v):
    EPS = 1e-8

    Gu = G.to_undirected()

    Nu = set(Gu.neighbors(u))
    Nv = set(Gu.neighbors(v))

    # common neighbors = triangles
    triangles = len(Nu & Nv)

    degree_u = len(Nu)
    degree_v = len(Nv)

    min_degree = min(degree_u - 1, degree_v - 1)

    if min_degree <= 0:
        return (triangles + 1) / (min_degree + EPS)

    return (triangles + 1) / min_degree


# Choose the generator points for the Voronoi partitioning. Each generator has the highest local density
# within a region of radius r. Distance calculations are done in a directed manner.
def _choose_generator_points(G, r, weighted_densities, all_pairs_distances):
    sorted_nodes = sorted(weighted_densities, key=weighted_densities.get, reverse=True)

    generator_points = []

    for node_i in sorted_nodes:
        is_largest = True
        lengths_i = all_pairs_distances[node_i]

        for node_j, distance in lengths_i.items():
            if node_j == node_i:
                continue

            if distance <= r:
                # Check if node_j has higher density or is already a generator
                # I was debugging this > to < for long
                if (
                    weighted_densities[node_i] < weighted_densities[node_j]
                    or node_j in generator_points
                ):
                    is_largest = False
                    break

        if is_largest:
            generator_points.append(node_i)

    return generator_points


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def voronoi_partitions(G, generator_points, all_pairs_distances=None, mode="out"):
    r"""Yield partitions for each circle with diameter r of the Voronoi Community Detection
    Algorithm.

    TODO: WRITE DOWN HOW THE ALGORITHM WORKS

    Parameters
    ----------
    G : NetworkX graph
    generator_points : list
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

    # check type of G, if undirected dont go in here
    if mode == "in":
        G_use = G.reverse()
    elif mode == "out":
        G_use = G
    else:
        G_use = G.to_undirected()

    membership = {node: -1 for node in G_use.nodes()}

    # If precomputed distances provided, use them
    if all_pairs_distances is not None:
        for node in G_use.nodes():
            min_distance = float("inf")
            closest_generator_idx = -1

            for generator_idx, generator in enumerate(generator_points):
                # Look up precomputed distance
                if (
                    generator in all_pairs_distances
                    and node in all_pairs_distances[generator]
                ):
                    distance = all_pairs_distances[generator][node]

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
                    G_use, generator, weight="weight"
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
