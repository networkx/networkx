import pytest
import networkx as nx
from networkx.algorithms.control.systems import *
import numpy as np


def test_directed_matching():
    G = nx.path_graph(5, create_using=nx.DiGraph)
    for t in range(1, len(G.edges) + 1):
        for edges in combinations(G.edges, t):
            assert is_directed_matching(edges)

    # Directed star graph
    edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
    G = nx.DiGraph()
    G.add_edges_from(edges)
    for t in range(2, len(G.edges) + 1):
        for edges in combinations(G.edges, t):
            assert not is_directed_matching(edges)


def test_lti_system():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(
        A, B, state_prefix="x", input_prefix="u"
    )

    states = ["x{}".format(i) for i in range(A.shape[0])]
    inputs = ["u{}".format(i) for i in range(B.shape[1])]
    edges = [
        ("x0", "x1"),
        ("x0", "x2"),
        ("x0", "x3"),
        ("x2", "x3"),
        ("x4", "x4"),
        ("u0", "x0"),
        ("u1", "x1"),
        ("u1", "x4"),
    ]
    edge_data = [
        ("x0", "x1", 1),
        ("x0", "x2", 2),
        ("x0", "x3", -1),
        ("x2", "x3", 3),
        ("x4", "x4", 4),
        ("u0", "x0", 5),
        ("u1", "x1", -2),
        ("u1", "x4", 6),
    ]

    assert sys.state_nodes == states
    assert sys.input_nodes == inputs
    assert list(sys.G.nodes) == states + inputs
    assert [e for e in sys.G.edges] == edges
    assert list(sys.G.edges.data("weight")) == edge_data

    G_A = nx.adjacency_matrix(sys.G, nodelist=states).todense().T
    G_B = nx.adjacency_matrix(sys.G).todense().T[: len(states), -len(inputs) :]
    assert (G_A == A).all()
    assert (G_B == B).all()


def test_controllability_matrix():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    true_C = np.array(
        [
            [5, 4, 0, 0, 0, 0, 0, 0, 0, 0],
            [5, 4, 5, 0, 5, 0, 5, 0, 5, 0],
            [5, 4, 10, 0, 20, 0, 40, 0, 80, 0],
            [5, 4, -5, 0, 5, 0, -5, 0, 5, 0],
            [5, 4, 0, 24, 0, 96, 0, 384, 0, 1536],
        ]
    )

    sys = nx.algorithms.control.systems.LTISystem(A, B)
    sys_C = sys.construct_controllability_matrix()

    assert (sys_C == true_C).all()
    assert sys.is_controllable()


def test_structural_controllability():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert not sys.is_inaccessible()
    assert not sys.contains_dilation()
    assert sys.is_structurally_controllable()

    A = np.array(
        [
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0],
        ]
    )
    B = np.array([[0], [0], [0], [0], [1]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert sys.is_inaccessible()
    assert sys.contains_dilation()
    assert not sys.is_structurally_controllable()


def test_strong_structural_controllability():
    A = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    B = np.array([[1], [0], [0]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    G = sys.G
    G_no_inputs = G.subgraph(sys.state_nodes)
    H = create_bipartite_from_directed_graph(G_no_inputs)
    assert nx.is_bipartite(H)
    assert not has_t_constrained_matching(H, 1)
    assert has_t_constrained_matching(H, 2)
    assert not has_t_constrained_matching(H, 3)

    G_x = add_self_loops(G_no_inputs)
    H_x = create_bipartite_from_directed_graph(G_x)
    assert not has_t_constrained_matching(H_x, 1, selfloops=False)
    assert has_t_constrained_matching(H_x, 2, selfloops=False)
    assert not has_t_constrained_matching(H_x, 3, selfloops=False)

    assert sys.is_strongly_structurally_controllable()

    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert not sys.is_strongly_structurally_controllable()


def test_driver_nodes():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    true_nodes = [{"x0", "x1"}, {"x0", "x2"}]
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert sys.find_minimum_driver_nodes() in true_nodes


def test_controllability_pbh():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [-1, 0, 3, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert sys.is_controllable_pbh()

    A = np.array(
        [
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0],
        ]
    )
    B = np.array([[0], [0], [0], [0], [1]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    assert not sys.is_controllable_pbh()


def test_minimum_actuators():

    A = np.array(
        [
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ]
    )
    B = np.array([[0], [0], [0], [0], [0], [0]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    actuators = sys.find_minimum_actuators()
    valids = [
        {"x0", "x1", "x2"},
        {"x0", "x1", "x3"},
        {"x0", "x1", "x4"},
        {"x0", "x1", "x5"},
    ]
    assert actuators in valids

    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 3, 0],
            [-1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    actuators = sys.find_minimum_actuators()
    valids = [{"x0", "x1", "x4"}, {"x0", "x3", "x4"}]
    assert actuators in valids


def test_link_importance():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 3, 0],
            [-1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    true_critical = {("x3", "x2"), ("x4", "x4")}
    true_redundant = {("x0", "x2")}
    true_ordinary = {("x0", "x1"), ("x0", "x3")}
    critical, redundant, ordinary = sys.classify_link_importance()
    assert critical == true_critical
    assert redundant == true_redundant
    assert ordinary == true_ordinary


def test_node_importance():
    A = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [2, 0, 0, 3, 0],
            [-1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4],
        ]
    )
    B = np.array([[5, 0], [0, -2], [0, 0], [0, 0], [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    true_critical = {"x0"}
    true_redundant = {"x2", "x4"}
    true_intermittent = {"x1", "x3"}
    critical, redundant, intermittent = sys.classify_node_importance()
    assert critical == true_critical
    assert redundant == true_redundant
    assert intermittent == true_intermittent


def test_node_deletion_importance():
    A = np.array(
        [
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
        ]
    )
    B = np.array([[0], [0], [0], [0]])
    sys = nx.algorithms.control.systems.LTISystem(A, B)
    true_critical = {"x1"}
    true_redundant = {"x0", "x3"}
    true_ordinary = {"x2"}
    critical, redundant, ordinary = sys.classify_node_deletion_importance()
    assert critical == true_critical
    assert redundant == true_redundant
    assert ordinary == true_ordinary
