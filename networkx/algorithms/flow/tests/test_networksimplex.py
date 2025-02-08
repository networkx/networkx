import bz2
import importlib.resources
import os
import pickle

import pytest

import networkx as nx
from networkx import NetworkXUnbounded


@pytest.fixture
def simple_flow_graph():
    G = nx.DiGraph()
    G.add_node("a", demand=0)
    G.add_node("b", demand=-5)
    G.add_node("c", demand=50000000)
    G.add_node("d", demand=-49999995)
    G.add_edge("a", "b", weight=3, capacity=4)
    G.add_edge("a", "c", weight=6, capacity=10)
    G.add_edge("b", "d", weight=1, capacity=9)
    G.add_edge("c", "d", weight=2, capacity=5)
    return G


@pytest.fixture
def simple_no_flow_graph():
    G = nx.DiGraph()
    G.add_node("s", demand=-5)
    G.add_node("t", demand=5)
    G.add_edge("s", "a", weight=1, capacity=3)
    G.add_edge("a", "b", weight=3)
    G.add_edge("a", "c", weight=-6)
    G.add_edge("b", "d", weight=1)
    G.add_edge("c", "d", weight=-2)
    G.add_edge("d", "t", weight=1, capacity=3)
    return G


def get_flowcost_from_flowdict(G, flowDict):
    """Returns flow cost calculated from flow dictionary"""
    flowCost = 0
    for u in flowDict:
        for v in flowDict[u]:
            flowCost += flowDict[u][v] * G[u][v]["weight"]
    return flowCost


def test_infinite_demand_raise(simple_flow_graph):
    G = simple_flow_graph
    inf = float("inf")
    node_name = "a"
    nx.set_node_attributes(G, {node_name: {"demand": inf}})
    with pytest.raises(
        nx.NetworkXError,
        match=f"Invalid input: Node '{node_name}' has an infinite absolute demand, which is not allowed.",
    ):
        nx.network_simplex(G)


def test_neg_infinite_demand_raise(simple_flow_graph):
    G = simple_flow_graph
    inf = float("inf")
    node_name = "a"
    nx.set_node_attributes(G, {node_name: {"demand": -inf}})
    with pytest.raises(
        nx.NetworkXError,
        match=f"Invalid input: Node '{node_name}' has an infinite absolute demand, which is not allowed.",
    ):
        nx.network_simplex(G)


def test_infinite_weight_raise(simple_flow_graph):
    G = simple_flow_graph
    inf = float("inf")
    nx.set_edge_attributes(
        G, {("a", "b"): {"weight": inf}, ("b", "d"): {"weight": inf}}
    )
    with pytest.raises(
        nx.NetworkXError,
        match=r"Invalid input: Edge .* has an infinite absolute weight, making the cost computation undefined.",
    ):
        nx.network_simplex(G)


def test_nonzero_net_demand_raise(simple_flow_graph):
    G = simple_flow_graph
    nx.set_node_attributes(G, {"b": {"demand": -4}})
    with pytest.raises(
        nx.NetworkXUnfeasible,
        match="Flow infeasible: The total supply does not match the total demand.",
    ):
        nx.network_simplex(G)


def test_negative_capacity_raise(simple_flow_graph):
    G = simple_flow_graph
    nx.set_edge_attributes(G, {("a", "b"): {"weight": 1}, ("b", "d"): {"capacity": -9}})
    with pytest.raises(
        nx.NetworkXUnfeasible,
        match=r"Invalid input: Edge .* has a negative capacity, which is not allowed.",
    ):
        nx.network_simplex(G)


def test_no_flow_satisfying_demands(simple_no_flow_graph):
    G = simple_no_flow_graph
    with pytest.raises(
        nx.NetworkXUnfeasible,
        match="Flow infeasible: The network cannot satisfy all node demands due to capacity constraints.",
    ):
        nx.network_simplex(G)


def test_sum_demands_not_zero(simple_no_flow_graph):
    G = simple_no_flow_graph
    nx.set_node_attributes(G, {"t": {"demand": 4}})
    with pytest.raises(
        nx.NetworkXUnfeasible,
        match="Flow infeasible: The total supply does not match the total demand.",
    ):
        nx.network_simplex(G)


def test_google_or_tools_example():
    """
    https://developers.google.com/optimization/flow/mincostflow
    """
    G = nx.DiGraph()
    start_nodes = [0, 0, 1, 1, 1, 2, 2, 3, 4]
    end_nodes = [1, 2, 2, 3, 4, 3, 4, 4, 2]
    capacities = [15, 8, 20, 4, 10, 15, 4, 20, 5]
    unit_costs = [4, 4, 2, 2, 6, 1, 3, 2, 3]
    supplies = [20, 0, 0, -5, -15]
    answer = 150

    for i in range(len(supplies)):
        G.add_node(i, demand=(-1) * supplies[i])  # supplies are negative of demand

    for i in range(len(start_nodes)):
        G.add_edge(
            start_nodes[i], end_nodes[i], weight=unit_costs[i], capacity=capacities[i]
        )

    flowCost, flowDict = nx.network_simplex(G)
    assert flowCost == answer
    assert flowCost == get_flowcost_from_flowdict(G, flowDict)


def test_google_or_tools_example2():
    """
    https://developers.google.com/optimization/flow/mincostflow
    """
    G = nx.DiGraph()
    start_nodes = [0, 0, 1, 1, 1, 2, 2, 3, 4, 3]
    end_nodes = [1, 2, 2, 3, 4, 3, 4, 4, 2, 5]
    capacities = [15, 8, 20, 4, 10, 15, 4, 20, 5, 10]
    unit_costs = [4, 4, 2, 2, 6, 1, 3, 2, 3, 4]
    supplies = [23, 0, 0, -5, -15, -3]
    answer = 183

    for i in range(len(supplies)):
        G.add_node(i, demand=(-1) * supplies[i])  # supplies are negative of demand

    for i in range(len(start_nodes)):
        G.add_edge(
            start_nodes[i], end_nodes[i], weight=unit_costs[i], capacity=capacities[i]
        )

    flowCost, flowDict = nx.network_simplex(G)
    assert flowCost == answer
    assert flowCost == get_flowcost_from_flowdict(G, flowDict)


def test_large():
    fname = (
        importlib.resources.files("networkx.algorithms.flow.tests")
        / "netgen-2.gpickle.bz2"
    )

    with bz2.BZ2File(fname, "rb") as f:
        G = pickle.load(f)
    flowCost, flowDict = nx.network_simplex(G)
    assert 6749969302 == flowCost
    assert 6749969302 == nx.cost_of_flow(G, flowDict)


def test_simple_digraph():
    G = nx.DiGraph()
    G.add_node("a", demand=-5)
    G.add_node("d", demand=5)
    G.add_edge("a", "b", weight=3, capacity=4)
    G.add_edge("a", "c", weight=6, capacity=10)
    G.add_edge("b", "d", weight=1, capacity=9)
    G.add_edge("c", "d", weight=2, capacity=5)
    flowCost, H = nx.network_simplex(G)
    soln = {"a": {"b": 4, "c": 1}, "b": {"d": 4}, "c": {"d": 1}, "d": {}}
    assert flowCost == 24
    assert nx.min_cost_flow_cost(G) == 24
    assert H == soln


def test_negcycle_infcap():
    G = nx.DiGraph()
    G.add_node("s", demand=-5)
    G.add_node("t", demand=5)
    G.add_edge("s", "a", weight=1, capacity=3)
    G.add_edge("a", "b", weight=3)
    G.add_edge("c", "a", weight=-6)
    G.add_edge("b", "d", weight=1)
    G.add_edge("d", "c", weight=-2)
    G.add_edge("d", "t", weight=1, capacity=3)
    pytest.raises(nx.NetworkXUnfeasible, nx.network_simplex, G)


def test_transshipment():
    G = nx.DiGraph()
    G.add_node("a", demand=1)
    G.add_node("b", demand=-2)
    G.add_node("c", demand=-2)
    G.add_node("d", demand=3)
    G.add_node("e", demand=-4)
    G.add_node("f", demand=-4)
    G.add_node("g", demand=3)
    G.add_node("h", demand=2)
    G.add_node("r", demand=3)
    G.add_edge("a", "c", weight=3)
    G.add_edge("r", "a", weight=2)
    G.add_edge("b", "a", weight=9)
    G.add_edge("r", "c", weight=0)
    G.add_edge("b", "r", weight=-6)
    G.add_edge("c", "d", weight=5)
    G.add_edge("e", "r", weight=4)
    G.add_edge("e", "f", weight=3)
    G.add_edge("h", "b", weight=4)
    G.add_edge("f", "d", weight=7)
    G.add_edge("f", "h", weight=12)
    G.add_edge("g", "d", weight=12)
    G.add_edge("f", "g", weight=-1)
    G.add_edge("h", "g", weight=-10)
    flowCost, H = nx.network_simplex(G)
    soln = {
        "a": {"c": 0},
        "b": {"a": 0, "r": 2},
        "c": {"d": 3},
        "d": {},
        "e": {"r": 3, "f": 1},
        "f": {"d": 0, "g": 3, "h": 2},
        "g": {"d": 0},
        "h": {"b": 0, "g": 0},
        "r": {"a": 1, "c": 1},
    }
    assert flowCost == 41
    assert H == soln


def test_digraph1():
    # From Bradley, S. P., Hax, A. C. and Magnanti, T. L. Applied
    # Mathematical Programming. Addison-Wesley, 1977.
    G = nx.DiGraph()
    G.add_node(1, demand=-20)
    G.add_node(4, demand=5)
    G.add_node(5, demand=15)
    G.add_edges_from(
        [
            (1, 2, {"capacity": 15, "weight": 4}),
            (1, 3, {"capacity": 8, "weight": 4}),
            (2, 3, {"weight": 2}),
            (2, 4, {"capacity": 4, "weight": 2}),
            (2, 5, {"capacity": 10, "weight": 6}),
            (3, 4, {"capacity": 15, "weight": 1}),
            (3, 5, {"capacity": 5, "weight": 3}),
            (4, 5, {"weight": 2}),
            (5, 3, {"capacity": 4, "weight": 1}),
        ]
    )
    flowCost, H = nx.network_simplex(G)
    soln = {
        1: {2: 12, 3: 8},
        2: {3: 8, 4: 4, 5: 0},
        3: {4: 11, 5: 5},
        4: {5: 10},
        5: {3: 0},
    }
    assert flowCost == 150
    assert nx.min_cost_flow_cost(G) == 150
    assert H == soln


def test_zero_capacity_edges():
    """Address issue raised in ticket #617 by arv."""
    G = nx.DiGraph()
    G.add_edges_from(
        [
            (1, 2, {"capacity": 1, "weight": 1}),
            (1, 5, {"capacity": 1, "weight": 1}),
            (2, 3, {"capacity": 0, "weight": 1}),
            (2, 5, {"capacity": 1, "weight": 1}),
            (5, 3, {"capacity": 2, "weight": 1}),
            (5, 4, {"capacity": 0, "weight": 1}),
            (3, 4, {"capacity": 2, "weight": 1}),
        ]
    )
    G.nodes[1]["demand"] = -1
    G.nodes[2]["demand"] = -1
    G.nodes[4]["demand"] = 2

    flowCost, H = nx.network_simplex(G)
    soln = {1: {2: 0, 5: 1}, 2: {3: 0, 5: 1}, 3: {4: 2}, 4: {}, 5: {3: 2, 4: 0}}
    assert flowCost == 6
    assert nx.min_cost_flow_cost(G) == 6
    assert H == soln


def test_digon():
    """Check if digons are handled properly. Taken from ticket
    #618 by arv."""
    nodes = [(1, {}), (2, {"demand": -4}), (3, {"demand": 4})]
    edges = [
        (1, 2, {"capacity": 3, "weight": 600000}),
        (2, 1, {"capacity": 2, "weight": 0}),
        (2, 3, {"capacity": 5, "weight": 714285}),
        (3, 2, {"capacity": 2, "weight": 0}),
    ]
    G = nx.DiGraph(edges)
    G.add_nodes_from(nodes)
    flowCost, H = nx.network_simplex(G)
    soln = {1: {2: 0}, 2: {1: 0, 3: 4}, 3: {2: 0}}
    assert flowCost == 2857140


def test_deadend():
    """Check if one-node cycles are handled properly. Taken from ticket
    #2906 from @sshraven."""
    G = nx.DiGraph()

    G.add_nodes_from(range(5), demand=0)
    G.nodes[4]["demand"] = -13
    G.nodes[3]["demand"] = 13

    G.add_edges_from([(0, 2), (0, 3), (2, 1)], capacity=20, weight=0.1)
    pytest.raises(nx.NetworkXUnfeasible, nx.network_simplex, G)


def test_infinite_capacity_neg_digon():
    """An infinite capacity negative cost digon results in an unbounded
    instance."""
    nodes = [(1, {}), (2, {"demand": -4}), (3, {"demand": 4})]
    edges = [
        (1, 2, {"weight": -600}),
        (2, 1, {"weight": 0}),
        (2, 3, {"capacity": 5, "weight": 714285}),
        (3, 2, {"capacity": 2, "weight": 0}),
    ]
    G = nx.DiGraph(edges)
    G.add_nodes_from(nodes)
    pytest.raises(nx.NetworkXUnbounded, nx.network_simplex, G)


def test_multidigraph():
    """Multidigraphs are acceptable."""
    G = nx.MultiDiGraph()
    G.add_weighted_edges_from([(1, 2, 1), (2, 3, 2)], weight="capacity")
    flowCost, H = nx.network_simplex(G)
    assert flowCost == 0
    assert H == {1: {2: {0: 0}}, 2: {3: {0: 0}}, 3: {}}


def test_negative_selfloops():
    """Negative selfloops should cause an exception if uncapacitated and
    always be saturated otherwise.
    """
    G = nx.DiGraph()
    G.add_edge(1, 1, weight=-1)
    pytest.raises(nx.NetworkXUnbounded, nx.network_simplex, G)

    G[1][1]["capacity"] = 2
    flowCost, H = nx.network_simplex(G)
    assert flowCost == -2
    assert H == {1: {1: 2}}

    G = nx.MultiDiGraph()
    G.add_edge(1, 1, "x", weight=-1)
    G.add_edge(1, 1, "y", weight=1)
    pytest.raises(nx.NetworkXUnbounded, nx.network_simplex, G)

    G[1][1]["x"]["capacity"] = 2
    flowCost, H = nx.network_simplex(G)
    assert flowCost == -2
    assert H == {1: {1: {"x": 2, "y": 0}}}


def test_bone_shaped():
    # From #1283
    G = nx.DiGraph()
    G.add_node(0, demand=-4)
    G.add_node(1, demand=2)
    G.add_node(2, demand=2)
    G.add_node(3, demand=4)
    G.add_node(4, demand=-2)
    G.add_node(5, demand=-2)
    G.add_edge(0, 1, capacity=4)
    G.add_edge(0, 2, capacity=4)
    G.add_edge(4, 3, capacity=4)
    G.add_edge(5, 3, capacity=4)
    G.add_edge(0, 3, capacity=0)
    flowCost, H = nx.network_simplex(G)
    assert flowCost == 0
    assert H == {0: {1: 2, 2: 2, 3: 0}, 1: {}, 2: {}, 3: {}, 4: {3: 2}, 5: {3: 2}}


def test_graphs_type_exceptions():
    G = nx.Graph()
    pytest.raises(nx.NetworkXNotImplemented, nx.network_simplex, G)
    G = nx.MultiGraph()
    pytest.raises(nx.NetworkXNotImplemented, nx.network_simplex, G)
    G = nx.DiGraph()
    pytest.raises(nx.NetworkXError, nx.network_simplex, G)


def create_graph(
    has_large_capacity: bool = False,
    has_large_weight: bool = False,
    has_large_demand: bool = False,
):
    large_value = 1000000000
    G = nx.DiGraph()

    # Add nodes with demands
    if has_large_demand:
        G.add_node("s0", demand=-large_value)
        G.add_node("c1", demand=large_value)
    else:
        G.add_node("s0", demand=-4)
        G.add_node("c1", demand=4)

    G.add_node("s1", demand=-4)
    G.add_node("ns", demand=0)
    G.add_node("nc", demand=0)
    G.add_node("c0", demand=4)

    # Add edges
    if has_large_capacity:
        G.add_edge("s0", "ns", weight=1, capacity=large_value)
    else:
        G.add_edge("s0", "ns")

    if has_large_weight:
        G.add_edge("s1", "ns", weight=large_value)
    else:
        G.add_edge("s1", "ns", weight=1)

    G.add_edge("ns", "nc", weight=1)
    G.add_edge("nc", "c0", weight=1)
    G.add_edge("nc", "c1", weight=1)

    return G


@pytest.mark.parametrize(
    "has_large_capacity, has_large_weight, has_large_demand",
    [
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
def test_network_simplex_large_capacities(
    has_large_capacity: bool, has_large_weight: bool, has_large_demand: bool
):
    """Address issues raised in ticket #7562."""
    graph = create_graph(has_large_capacity, has_large_weight, has_large_demand)
    flow_value, flow_dict = nx.network_simplex(graph)


def test_network_simplex_unbounded_flow():
    G = nx.DiGraph()
    # Add nodes
    G.add_node("A")
    G.add_node("B")
    G.add_node("C")

    # Add edges forming a negative cycle
    G.add_edge("A", "B", weight=-5)
    G.add_edge("B", "C", weight=-5)
    G.add_edge("C", "A", weight=-5)

    with pytest.raises(
        NetworkXUnbounded,
        match="Unbounded flow detected: A negative-weight cycle with infinite capacity allows indefinite cost reduction.",
    ):
        nx.network_simplex(G)
