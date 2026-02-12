from collections import Counter

import networkx as nx
import pytest

from networkx.algorithms.planarity import faces_from_planar_embedding


def _directed_half_edges_from_embedding(embedding):
    edges = []
    for u in embedding:
        for v in embedding.neighbors_cw_order(u):
            edges.append((u, v))
    return edges


def _directed_half_edges_from_faces(faces):
    edges = []
    for face in faces:
        if not face:
            continue
        for i, u in enumerate(face):
            v = face[(i + 1) % len(face)]
            edges.append((u, v))
    return edges


def _assert_half_edge_partition(embedding, faces):
    face_half_edges = _directed_half_edges_from_faces(faces)
    embedding_half_edges = _directed_half_edges_from_embedding(embedding)
    assert Counter(face_half_edges) == Counter(embedding_half_edges)
    assert all(count == 1 for count in Counter(face_half_edges).values())


def _embedding_for_graph(graph):
    is_planar, embedding = nx.check_planarity(graph)
    assert is_planar
    return embedding


def test_cycle_graph_faces_and_half_edge_partition():
    graph = nx.cycle_graph(4)
    embedding = _embedding_for_graph(graph)

    faces = faces_from_planar_embedding(embedding)

    assert len(faces) == 2
    _assert_half_edge_partition(embedding, faces)


def test_tree_has_single_face_walk_with_repeated_vertices():
    graph = nx.path_graph(4)
    embedding = _embedding_for_graph(graph)

    faces = faces_from_planar_embedding(embedding)

    assert len(faces) == 1
    assert len(faces[0]) == 2 * graph.number_of_edges()
    assert len(set(faces[0])) < len(faces[0])
    _assert_half_edge_partition(embedding, faces)


def test_k4_faces_match_euler_formula():
    graph = nx.complete_graph(4)
    embedding = _embedding_for_graph(graph)

    faces = faces_from_planar_embedding(embedding)

    assert len(faces) == graph.number_of_edges() - graph.number_of_nodes() + 2
    assert sorted(len(face) for face in faces) == [3, 3, 3, 3]
    _assert_half_edge_partition(embedding, faces)


def test_disconnected_components_return_component_local_boundary_walks():
    graph = nx.disjoint_union(nx.cycle_graph(3), nx.cycle_graph(3))
    embedding = _embedding_for_graph(graph)

    faces = faces_from_planar_embedding(embedding)

    assert len(faces) == 4
    _assert_half_edge_partition(embedding, faces)


def test_isolated_nodes_have_no_faces():
    graph = nx.empty_graph(5)
    embedding = _embedding_for_graph(graph)
    faces = faces_from_planar_embedding(embedding)
    assert faces == []


def test_non_embedding_input_raises_type_error():
    with pytest.raises(TypeError):
        faces_from_planar_embedding(nx.Graph())
