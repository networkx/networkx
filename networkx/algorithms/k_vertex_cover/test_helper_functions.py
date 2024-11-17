from itertools import combinations

import networkx as nx
from networkx.algorithms.k_vertex_cover.k_vertex_cover import (
    is_vertex_cover,
    k_vertex_cover,
)


def test_vertex_cover(G: nx.Graph, k: int):
    # print(f"Graph : {G}")
    # print(f"Parameter : {k}")

    is_vc, vertex_cover = k_vertex_cover(G, k)
    min_vc_length = find_min_vertex_cover(G)

    # if min_vc_length is less than or equal to k, then algorithm must return a valid vertex cover
    # else, the algorigthm must return False
    if min_vc_length <= k:
        assert is_vc
        assert (
            len(vertex_cover) <= k
        ), f"Vertex cover size must be less than or equal to k={k}"
        assert (
            len(vertex_cover) >= min_vc_length
        ), f"Vertex cover must be atleast min_vc_length={min_vc_length}"
        assert is_vertex_cover(
            G, vertex_cover
        ), "The output must be a vertex cover for the graph"
    else:
        assert not is_vc
        assert not is_vertex_cover(
            G.copy(), vertex_cover
        ), "The output must not be a vertex cover for G"


def generate_subset_of_vertices(G: nx.Graph):
    nodes = list(G.nodes)
    n = len(nodes)

    for r in range(n + 1):
        yield from combinations(nodes, r)


def find_min_vertex_cover(G: nx.Graph):
    nodes = list(G.nodes)
    vertices_subset = generate_subset_of_vertices(G)
    while True:
        try:
            vc_candidate = set(next(vertices_subset))
            if is_vertex_cover(G, vc_candidate):
                vertices_subset.close()
                return len(vc_candidate)
        except:
            break

    return len(nodes)
